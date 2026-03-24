"""Flask web UI for Kundli."""
from flask import Flask, render_template, request, jsonify, session as flask_session
from datetime import datetime, timedelta, timezone
from geopy.geocoders import Nominatim
import json
import os
import tempfile
import time as _time
import uuid
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

from kundli.calc import (
    to_julian, compute_planets, compute_houses,
    compute_dasha, compute_antardasha, compute_pratyantar,
    compute_aspects, check_yogas, SIGNS,
    build_planet_house_map, compute_divisional_chart, DIVISIONAL_CHARTS,
)
from kundli.readings import build_house_readings
from kundli.names import PLANET_NAMES, SIGN_NAMES, PLANET_ABBR
from kundli.chatbot import chat as chatbot_chat
from kundli.match import compute_ashtakoota
from kundli.lifeareas import generate_life_areas

app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.secret_key = os.environ.get("KUNDLI_SECRET_KEY", "change-me-in-production")


@app.before_request
def _log_request_start():
    request._start_time = _time.time()


@app.after_request
def _log_request_end(response):
    duration = _time.time() - getattr(request, "_start_time", _time.time())
    if request.path != "/health":
        logging.info(f"{request.method} {request.path} {response.status_code} {duration:.3f}s")
    return response

# File-based chart store so it works across multiple gunicorn workers
_CHART_DIR = os.path.join(tempfile.gettempdir(), "kundli_charts")
os.makedirs(_CHART_DIR, exist_ok=True)
_CHART_TTL = 3600  # 1 hour


class ChartStore:
    """File-based TTL cache for chart contexts. Works across workers."""

    def set(self, key, value):
        self._evict()
        path = os.path.join(_CHART_DIR, f"{key}.json")
        payload = {"data": self._serialize(value), "ts": _time.time()}
        with open(path, "w") as f:
            json.dump(payload, f)

    def get(self, key):
        path = os.path.join(_CHART_DIR, f"{key}.json")
        if not os.path.exists(path):
            return None
        try:
            with open(path) as f:
                payload = json.load(f)
        except (json.JSONDecodeError, OSError):
            return None
        if _time.time() - payload["ts"] > _CHART_TTL:
            os.remove(path)
            return None
        return self._deserialize(payload["data"])

    def _evict(self):
        now = _time.time()
        try:
            entries = sorted(
                ((f, os.path.join(_CHART_DIR, f)) for f in os.listdir(_CHART_DIR) if f.endswith(".json")),
                key=lambda x: os.path.getmtime(x[1]),
            )
        except OSError:
            return
        for name, path in entries:
            try:
                if now - os.path.getmtime(path) > _CHART_TTL:
                    os.remove(path)
            except OSError:
                pass
        # Cap at 100 entries
        remaining = [p for _, p in entries if os.path.exists(p)]
        while len(remaining) > 100:
            try:
                os.remove(remaining.pop(0))
            except OSError:
                pass

    @staticmethod
    def _serialize(ctx):
        """Convert chart context to JSON-safe dict (datetimes → ISO strings)."""
        out = dict(ctx)
        out["planets"] = ctx["planets"]
        out["houses"] = ctx["houses"]

        def _ser_period(d):
            s = {**d, "start": d["start"].isoformat(), "end": d["end"].isoformat()}
            if "antardasha" in d:
                s["antardasha"] = [_ser_period(a) for a in d["antardasha"]]
            if "pratyantar" in d:
                s["pratyantar"] = [_ser_period(p) for p in d["pratyantar"]]
            return s

        out["dashas"] = [_ser_period(d) for d in ctx["dashas"]]
        return out

    @staticmethod
    def _deserialize(data):
        """Restore chart context from JSON (ISO strings → datetimes)."""

        def _deser_period(d):
            d["start"] = datetime.fromisoformat(d["start"])
            d["end"] = datetime.fromisoformat(d["end"])
            if "antardasha" in d:
                d["antardasha"] = [_deser_period(a) for a in d["antardasha"]]
            if "pratyantar" in d:
                d["pratyantar"] = [_deser_period(p) for p in d["pratyantar"]]
            return d

        data["dashas"] = [_deser_period(d) for d in data["dashas"]]
        return data


_chart_store = ChartStore()


_geo_cache = {}


def get_coordinates(location):
    normalized = location.strip().lower()
    if normalized in _geo_cache:
        return _geo_cache[normalized]
    try:
        geo = Nominatim(user_agent="kundli_app", timeout=10)
        loc = geo.geocode(location)
        if not loc:
            return None, None
        result = (loc.latitude, loc.longitude)
        _geo_cache[normalized] = result
        return result
    except Exception:
        return None, None


def build_chart_data(planets, houses):
    asc_idx = SIGNS.index(houses[0]["sign"])
    chart = {}
    for i in range(12):
        sign = SIGNS[(asc_idx + i) % 12]
        pls_hindu = [PLANET_ABBR["hindu"][p["planet"]] for p in planets if p["sign"] == sign]
        pls_eng = [PLANET_ABBR["english"][p["planet"]] for p in planets if p["sign"] == sign]
        chart[i + 1] = {
            "sign_h": sign[:3],
            "sign_e": SIGN_NAMES.get(sign, sign)[:3],
            "planets_h": " ".join(pls_hindu),
            "planets_e": " ".join(pls_eng),
        }
    return chart


@app.route("/health")
def health():
    checks = {"status": "ok"}
    # Verify Swiss Ephemeris is functional
    try:
        import swisseph as swe
        test_jd = swe.julday(2000, 1, 1, 12.0)
        swe.calc_ut(test_jd, swe.SUN)
        checks["ephemeris"] = "ok"
    except Exception as e:
        checks["ephemeris"] = str(e)
        checks["status"] = "degraded"
    # Check chart store is writable
    try:
        test_path = os.path.join(_CHART_DIR, ".healthcheck")
        with open(test_path, "w") as f:
            f.write("ok")
        os.remove(test_path)
        checks["chart_store"] = "ok"
    except Exception as e:
        checks["chart_store"] = str(e)
        checks["status"] = "degraded"
    status_code = 200 if checks["status"] == "ok" else 503
    return jsonify(checks), status_code


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")

    date_str = request.form.get("date", "").strip()
    time_str = request.form.get("time", "").strip()
    location = request.form.get("location", "").strip()
    tz_str = request.form.get("tz", "5.5").strip()

    if not date_str or not time_str or not location:
        return render_template("index.html", error="All fields are required.")

    try:
        year, month, day = map(int, date_str.split("-"))
        hour, minute = map(int, time_str.split(":"))
        birth_dt = datetime(year, month, day, hour, minute)
        if not (1 <= year <= 2100):
            raise ValueError("Year out of supported range (1-2100)")
    except (ValueError, TypeError) as e:
        return render_template("index.html", error=f"Invalid date or time: {e}")

    try:
        tz = float(tz_str)
        if not -12 <= tz <= 14:
            raise ValueError
    except (ValueError, TypeError):
        return render_template("index.html", error="Invalid timezone offset.")

    lat, lon = get_coordinates(location)
    if lat is None:
        return render_template("index.html", error=f"Could not find location: {location}")

    logging.info(f"Generating chart: {birth_dt.isoformat()} at {location} ({tz})")
    try:
        jd = to_julian(birth_dt, tz)
        planets = compute_planets(jd)
        houses = compute_houses(jd, lat, lon)
    except Exception as e:
        logging.exception("Chart computation failed")
        return render_template("index.html", error=f"Could not compute chart: {e}")

    now = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=tz)

    # Precompute shared data once
    planet_house_map = build_planet_house_map(planets, houses)
    moon = next(p for p in planets if p["planet"] == "Chandra")
    dashas = compute_dasha(moon["longitude"], birth_dt)
    dashas = compute_antardasha(dashas)
    dashas = compute_pratyantar(dashas)
    aspects = compute_aspects(planets)
    yogas = check_yogas(planets, houses)
    chart_data = build_chart_data(planets, houses)
    house_readings, current_dasha = build_house_readings(planets, houses, dashas, now, planet_house_map)
    life_areas = generate_life_areas(planets, houses, dashas, current_dasha, planet_house_map)

    # Divisional charts (skip D-1, that's the birth chart)
    varga_charts = []
    for key, info in DIVISIONAL_CHARTS.items():
        if info["div"] == 1:
            continue
        div_planets = compute_divisional_chart(planets, info["div"])
        # Build South Indian style chart data
        chart_cells = {}
        for si in range(12):
            sign = SIGNS[si]
            pls_h = [PLANET_ABBR["hindu"][p["planet"]] for p in div_planets if p["sign"] == sign]
            pls_e = [PLANET_ABBR["english"][p["planet"]] for p in div_planets if p["sign"] == sign]
            chart_cells[si] = {
                "sign_h": sign[:3],
                "sign_e": SIGN_NAMES.get(sign, sign)[:3],
                "planets_h": " ".join(pls_h),
                "planets_e": " ".join(pls_e),
            }
        varga_charts.append({
            "key": key, "name": info["name"], "desc": info["desc"],
            "planets": div_planets, "chart_cells": chart_cells,
        })

    # Store chart context for chatbot
    chart_id = uuid.uuid4().hex[:8]
    _chart_store.set(chart_id, {
        "house_readings": house_readings,
        "current_dasha": current_dasha,
        "planet_names": PLANET_NAMES,
        "planets": planets,
        "houses": houses,
        "dashas": dashas,
        "tz_offset": tz,
    })
    flask_session["chart_id"] = chart_id

    return render_template("result.html",
        birth_dt=birth_dt, location=location, lat=lat, lon=lon,
        lagna=houses[0], planets=planets, houses=houses,
        dashas=dashas, aspects=aspects, yogas=yogas,
        chart=chart_data, house_readings=house_readings,
        current_dasha=current_dasha, now=now,
        planet_names=PLANET_NAMES, sign_names=SIGN_NAMES,
        life_areas=life_areas,
        varga_charts=varga_charts,
    )


@app.route("/match", methods=["POST"])
def match():
    errors = []
    people = []
    for i in ("1", "2"):
        date_str = request.form.get(f"date{i}", "").strip()
        time_str = request.form.get(f"time{i}", "").strip()
        location = request.form.get(f"location{i}", "").strip()
        tz_str = request.form.get(f"tz{i}", "5.5").strip()
        name = request.form.get(f"name{i}", "").strip() or f"Person {i}"
        if not date_str or not time_str or not location:
            errors.append(f"All fields required for Person {i}.")
            continue
        try:
            year, month, day = map(int, date_str.split("-"))
            hour, minute = map(int, time_str.split(":"))
            birth_dt = datetime(year, month, day, hour, minute)
            tz = float(tz_str)
        except (ValueError, TypeError):
            errors.append(f"Invalid date/time for Person {i}.")
            continue
        lat, lon = get_coordinates(location)
        if lat is None:
            errors.append(f"Could not find location: {location}")
            continue
        jd = to_julian(birth_dt, tz)
        planets = compute_planets(jd)
        moon = next(p for p in planets if p["planet"] == "Chandra")
        nak_idx = int(moon["longitude"] // (360 / 27))
        people.append({"name": name, "moon_sign": moon["sign"], "nakshatra": moon["nakshatra"], "nak_idx": nak_idx})

    if errors:
        return render_template("index.html", match_error="; ".join(errors), tab="match")
    if len(people) < 2:
        return render_template("index.html", match_error="Both persons required.", tab="match")

    result = compute_ashtakoota(people[0]["nak_idx"], people[1]["nak_idx"])
    return render_template("match_result.html", result=result, people=people, planet_names=PLANET_NAMES, sign_names=SIGN_NAMES)


@app.route("/chat", methods=["POST"])
def chat_endpoint():
    data = request.get_json()
    if not data:
        return jsonify({"answer": "Invalid request."}), 400
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"answer": "Please ask a question."})

    chart_id = flask_session.get("chart_id")
    ctx = _chart_store.get(chart_id) if chart_id else None
    has_ctx = ctx is not None

    logging.info(f"Chat: chart_id={chart_id} has_ctx={has_ctx} q={question!r}")
    answer = chatbot_chat(question, ctx)
    return jsonify({"answer": answer})


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG", "0") == "1", port=int(os.environ.get("PORT", 8080)))
