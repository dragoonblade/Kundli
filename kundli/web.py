"""Flask web UI for Kundli."""
from flask import Flask, render_template, request, jsonify, session as flask_session
from datetime import datetime, timedelta, timezone
import json
import os
import time as _time
import uuid
from urllib.parse import quote
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
if os.environ.get("LOG_FORMAT") == "json":
    import json as _json

    class _JsonFormatter(logging.Formatter):
        def format(self, record):
            return _json.dumps({"ts": self.formatTime(record), "level": record.levelname, "msg": record.getMessage()})

    _handler = logging.StreamHandler()
    _handler.setFormatter(_JsonFormatter())
    logging.root.handlers = [_handler]

from kundli.calc import (
    to_julian, compute_planets, compute_houses,
    compute_dasha, compute_antardasha, compute_pratyantar,
    compute_aspects, check_yogas, check_doshas, SIGNS,
    build_planet_house_map, compute_divisional_chart, DIVISIONAL_CHARTS,
    compute_shadbala,
)
from kundli.readings import build_house_readings
from kundli.names import PLANET_NAMES, SIGN_NAMES, PLANET_ABBR
from kundli.chatbot import chat as chatbot_chat
from kundli.match import compute_ashtakoota
from kundli.lifeareas import generate_life_areas
from kundli.pdf import generate_kundli_pdf, generate_match_pdf
from kundli.remedies import DOSHA_REMEDIES, PLANET_REMEDIES, UNIVERSAL_REMEDIES
from kundli.ashtakavarga import compute_ashtakavarga
from kundli.insights import generate_daily_insights
from kundli.geo import get_coordinates
from kundli.predictor import compute_event_periods
from kundli.prashna import analyze_prashna
from kundli.panchang import compute_panchang

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.secret_key = os.environ.get("KUNDLI_SECRET_KEY", "change-me-in-production")
if app.secret_key == "change-me-in-production":  # nosec B105
    logging.warning("KUNDLI_SECRET_KEY not set. Using insecure fallback. Set it in production.")

limiter = Limiter(get_remote_address, app=app, default_limits=["60 per minute"], storage_uri="memory://")
GA4_ID = os.environ.get("GA4_ID", "")
SITE_URL = os.environ.get("SITE_URL", "https://kundli-2c3b.onrender.com")


@app.context_processor
def _inject_globals():
    return {"ga4_id": GA4_ID, "universal_remedies": UNIVERSAL_REMEDIES, "site_url": SITE_URL}


@limiter.request_filter
def _no_limit_in_tests():
    return app.config.get("TESTING", False)


@app.after_request
def _security_headers(response):
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if not app.debug:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://www.google-analytics.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https://www.google-analytics.com https://www.googletagmanager.com; connect-src 'self' https://www.google-analytics.com https://*.google-analytics.com https://*.analytics.google.com https://www.googletagmanager.com;"
    return response


@app.before_request
def _log_request_start():
    request._start_time = _time.time()
    request._request_id = uuid.uuid4().hex[:8]


@app.after_request
def _log_request_end(response):
    duration = _time.time() - getattr(request, "_start_time", _time.time())
    rid = getattr(request, "_request_id", "-")
    if request.path != "/health":
        logging.info(f"[{rid}] {request.method} {request.path} {response.status_code} {duration:.3f}s")
    response.headers["X-Request-ID"] = rid
    return response

from kundli.store import ChartStore, _CHART_DIR

_chart_store = ChartStore()


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


def _get_panchang():
    """Compute today's panchang."""
    from kundli.core import to_julian
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    jd = to_julian(now, 0)
    panchang = compute_panchang(jd)
    return panchang, now.strftime("%d %B %Y")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        if request.args.get("d"):
            return _generate_chart(
                request.args.get("d"), request.args.get("t", ""),
                request.args.get("l", ""), request.args.get("z", "5.5"),
            )
        panchang, today_str = _get_panchang()
        return render_template("index.html", last_chart=flask_session.get("last_chart"), panchang=panchang, today_str=today_str)

    return _generate_chart(
        request.form.get("date", "").strip(),
        request.form.get("time", "").strip(),
        request.form.get("location", "").strip(),
        request.form.get("tz", "5.5").strip(),
    )


def _build_varga_charts(planets):
    """Build divisional chart data for all Varga charts except D-1."""
    varga_charts = []
    for key, info in DIVISIONAL_CHARTS.items():
        if info["div"] == 1:
            continue
        div_planets = compute_divisional_chart(planets, info["div"])
        chart_cells = {}
        for si in range(12):
            sign = SIGNS[si]
            pls_h = [PLANET_ABBR["hindu"][p["planet"]] for p in div_planets if p["sign"] == sign]
            pls_e = [PLANET_ABBR["english"][p["planet"]] for p in div_planets if p["sign"] == sign]
            chart_cells[si] = {
                "sign_h": sign[:3], "sign_e": SIGN_NAMES.get(sign, sign)[:3],
                "planets_h": " ".join(pls_h), "planets_e": " ".join(pls_e),
            }
        varga_charts.append({"key": key, "name": info["name"], "desc": info["desc"], "planets": div_planets, "chart_cells": chart_cells})
    return varga_charts


def _compute_transits(now, houses):
    """Compute current transit positions mapped to natal houses."""
    current_jd = to_julian(now, 0)
    current_planets = compute_planets(current_jd)
    natal_asc_idx = SIGNS.index(houses[0]["sign"])
    transits = []
    for tp in current_planets:
        tp_sign_idx = SIGNS.index(tp["sign"])
        transit_house = (tp_sign_idx - natal_asc_idx) % 12 + 1
        transits.append({"planet": tp["planet"], "sign": tp["sign"], "degree": tp["degree"], "house": transit_house})
    current_saturn_sign = next(p["sign"] for p in current_planets if p["planet"] == "Shani")
    return transits, current_saturn_sign


def _generate_chart(date_str, time_str, location, tz_str):
    form_vals = {"prev_date": date_str, "prev_time": time_str, "prev_location": location, "prev_tz": tz_str}

    if not date_str or not time_str or not location:
        return render_template("index.html", error="All fields are required.", **form_vals)

    try:
        year, month, day = map(int, date_str.split("-"))
        hour, minute = map(int, time_str.split(":"))
        birth_dt = datetime(year, month, day, hour, minute)
        if not (1 <= year <= 2100):
            raise ValueError("Year out of supported range (1-2100)")
    except (ValueError, TypeError) as e:
        return render_template("index.html", error=f"Invalid date or time: {e}", **form_vals)

    try:
        tz = float(tz_str)
        if not -12 <= tz <= 14:
            raise ValueError
    except (ValueError, TypeError):
        return render_template("index.html", error="Invalid timezone offset.", **form_vals)

    lat, lon = get_coordinates(location)
    if lat is None:
        return render_template("index.html", error=f"Could not find location: {location}. Try a nearby major city or check the spelling.", **form_vals)

    logging.info(f"Generating chart: {birth_dt.isoformat()} at {location} ({tz})")
    try:
        jd = to_julian(birth_dt, tz)
        planets = compute_planets(jd)
        houses = compute_houses(jd, lat, lon)
    except Exception as e:
        logging.exception("Chart computation failed")
        return render_template("index.html", error=f"Could not compute chart: {e}", **form_vals)

    now = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=tz)

    # Precompute shared data once
    planet_house_map = build_planet_house_map(planets, houses)
    moon = next(p for p in planets if p["planet"] == "Chandra")
    dashas = compute_dasha(moon["longitude"], birth_dt)
    dashas = compute_antardasha(dashas)
    dashas = compute_pratyantar(dashas)
    aspects = compute_aspects(planets)
    yogas = check_yogas(planets, houses, planet_house_map)
    shadbala = compute_shadbala(planets, houses, planet_house_map)
    ashtakavarga = compute_ashtakavarga(planets, houses)
    # Current transit positions for Sade Sati + Gochar
    transits, current_saturn_sign = _compute_transits(now, houses)
    doshas = check_doshas(planets, planet_house_map, current_saturn_sign)
    daily_insights = generate_daily_insights(transits)
    event_periods = compute_event_periods(dashas, houses, tz)
    chart_data = build_chart_data(planets, houses)
    house_readings, current_dasha = build_house_readings(planets, houses, dashas, now, planet_house_map)
    life_areas = generate_life_areas(planets, houses, dashas, current_dasha, planet_house_map)
    varga_charts = _build_varga_charts(planets)

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
        "yogas": yogas,
        "doshas": doshas,
        "birth_dt": birth_dt.isoformat(),
        "location": location,
    })
    flask_session["chart_id"] = chart_id
    flask_session["last_chart"] = {"date": date_str, "time": time_str, "location": location, "tz": tz_str}

    return render_template("result.html",
        birth_dt=birth_dt, location=location, lat=lat, lon=lon,
        lagna=houses[0], planets=planets, houses=houses,
        dashas=dashas, aspects=aspects, yogas=yogas, doshas=doshas, shadbala=shadbala, ashtakavarga=ashtakavarga,
        chart=chart_data, house_readings=house_readings,
        current_dasha=current_dasha, now=now,
        planet_names=PLANET_NAMES, sign_names=SIGN_NAMES,
        life_areas=life_areas,
        varga_charts=varga_charts,
        dosha_remedies=DOSHA_REMEDIES, planet_remedies=PLANET_REMEDIES,
        share_url=f"/?d={date_str}&t={time_str}&l={quote(location)}&z={tz_str}",
        transits=transits, daily_insights=daily_insights,
        event_periods=event_periods,
    )


@app.route("/match", methods=["POST"])
@limiter.limit("10 per minute")
def match():
    # Preserve form inputs for error redisplay
    form_vals = {}
    for i in ("1", "2"):
        for field in ("name", "date", "time", "location", "tz"):
            form_vals[f"prev_{field}{i}"] = request.form.get(f"{field}{i}", "").strip()

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
            errors.append(f"Could not find location: {location}. Try a nearby major city.")
            continue
        jd = to_julian(birth_dt, tz)
        planets = compute_planets(jd)
        houses = compute_houses(jd, lat, lon)
        moon = next(p for p in planets if p["planet"] == "Chandra")
        sun = next(p for p in planets if p["planet"] == "Surya")
        nak_idx = int(moon["longitude"] // (360 / 27))
        phm = build_planet_house_map(planets, houses)
        mars_house = phm.get("Mangal")
        is_manglik = mars_house in (1, 2, 4, 7, 8, 12)
        # Current dasha
        dashas = compute_dasha(moon["longitude"], birth_dt)
        now_local = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=tz)
        current_md = next((d["lord"] for d in dashas if d["start"] <= now_local <= d["end"]), None)
        people.append({
            "name": name, "moon_sign": moon["sign"], "nakshatra": moon["nakshatra"],
            "sun_sign": sun["sign"], "lagna": houses[0]["sign"],
            "nak_idx": nak_idx, "manglik": is_manglik, "mars_house": mars_house,
            "current_dasha": current_md,
            "chart_url": f"/?d={date_str}&t={time_str}&l={quote(location)}&z={tz_str}",
        })

    if errors:
        return render_template("index.html", match_error="; ".join(errors), tab="match", **form_vals)
    if len(people) < 2:
        return render_template("index.html", match_error="Both persons required.", tab="match", **form_vals)

    result = compute_ashtakoota(people[0]["nak_idx"], people[1]["nak_idx"])
    flask_session["match_result"] = {"result": result, "people": people}
    return render_template("match_result.html", result=result, people=people, planet_names=PLANET_NAMES, sign_names=SIGN_NAMES)


@app.route("/pdf", methods=["GET"])
def pdf_download():
    chart_id = flask_session.get("chart_id")
    ctx = _chart_store.get(chart_id) if chart_id else None
    if not ctx:
        return "No chart found. Generate a Kundli first.", 404
    pdf_bytes = generate_kundli_pdf(ctx)
    return pdf_bytes, 200, {
        "Content-Type": "application/pdf",
        "Content-Disposition": "attachment; filename=kundli.pdf",
    }


@app.route("/match/pdf", methods=["GET"])
def match_pdf_download():
    """Generate match PDF from session data."""
    data = flask_session.get("match_result")
    if not data:
        return "No match found. Run a compatibility check first.", 404
    pdf_bytes = generate_match_pdf(data["result"], data["people"])
    return pdf_bytes, 200, {
        "Content-Type": "application/pdf",
        "Content-Disposition": "attachment; filename=kundli-match.pdf",
    }



@app.route("/api/chart", methods=["POST"])
@limiter.limit("20 per minute")
def api_chart():
    """REST API: generate chart from JSON input, return JSON output."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body required"}), 400
    date_str = data.get("date", "")
    time_str = data.get("time", "")
    location = data.get("location", "")
    tz_val = data.get("tz", 5.5)
    if not all([date_str, time_str, location]):
        return jsonify({"error": "date, time, location required"}), 400
    try:
        year, month, day = map(int, date_str.split("-"))
        hour, minute = map(int, time_str.split(":"))
        birth_dt = datetime(year, month, day, hour, minute)
        tz = float(tz_val)
    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid input: {e}"}), 400
    lat, lon = get_coordinates(location)
    if lat is None:
        return jsonify({"error": f"Could not find location: {location}"}), 400
    try:
        jd = to_julian(birth_dt, tz)
        planets = compute_planets(jd)
        houses = compute_houses(jd, lat, lon)
        planet_house_map = build_planet_house_map(planets, houses)
        moon = next(p for p in planets if p["planet"] == "Chandra")
        dashas = compute_dasha(moon["longitude"], birth_dt)
        yogas = check_yogas(planets, houses, planet_house_map)
    except Exception as e:
        logging.exception("API chart computation failed")
        return jsonify({"error": f"Computation failed: {e}"}), 500
    return jsonify({
        "birth": {"date": date_str, "time": time_str, "location": location, "tz": tz, "lat": lat, "lon": lon},
        "lagna": {"sign": houses[0]["sign"], "degree": houses[0]["degree"]},
        "planets": planets,
        "houses": houses,
        "dashas": [{"lord": d["lord"], "start": d["start"].isoformat(), "end": d["end"].isoformat(), "years": d["years"]} for d in dashas],
        "yogas": yogas,
    })

@app.route("/prashna", methods=["POST"])
@limiter.limit("10 per minute")
def prashna():
    """Prashna Kundli: cast chart for current moment to answer a question."""
    question = request.form.get("question", "").strip()
    category = request.form.get("category", "general").strip()
    location = request.form.get("prashna_location", "").strip()
    tz_str = request.form.get("prashna_tz", "5.5").strip()

    if not question or not location:
        return render_template("index.html", prashna_error="Question and location are required.", tab="prashna")

    try:
        tz = float(tz_str)
    except (ValueError, TypeError):
        return render_template("index.html", prashna_error="Invalid timezone.", tab="prashna")

    lat, lon = get_coordinates(location)
    if lat is None:
        return render_template("index.html", prashna_error=f"Could not find location: {location}. Try a nearby major city.", tab="prashna")

    now = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=tz)
    jd = to_julian(now, tz)
    planets = compute_planets(jd)
    houses = compute_houses(jd, lat, lon)
    result = analyze_prashna(planets, houses, category)

    return render_template("prashna_result.html",
        result=result, question=question, cast_time=now, location=location,
        planets=planets, houses=houses,
        planet_names=PLANET_NAMES, sign_names=SIGN_NAMES,
    )


@app.route("/faq")
def faq():
    return render_template("faq.html")


@app.route("/sitemap.xml")
def sitemap():
    return app.send_static_file("sitemap.xml")


@app.route("/robots.txt")
def robots():
    return app.send_static_file("robots.txt")


@app.route("/llms.txt")
def llms_txt():
    return app.send_static_file("llms.txt")


@app.route("/llms-full.txt")
def llms_full_txt():
    return app.send_static_file("llms-full.txt")


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
