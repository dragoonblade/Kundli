"""Flask web UI for Kundli."""
from flask import Flask, render_template, request, jsonify, session as flask_session
from datetime import datetime
from geopy.geocoders import Nominatim
import os
import uuid
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

from kundli.calc import (
    to_julian, compute_planets, compute_houses,
    compute_dasha, compute_aspects, check_yogas, SIGNS,
    build_planet_house_map, compute_divisional_chart, DIVISIONAL_CHARTS,
)
from kundli.readings import (
    HOUSE_THEMES, build_house_readings,
)
from kundli.names import PLANET_NAMES, SIGN_NAMES, PLANET_ABBR, SIGN_ABBR, SIGN_LORDS
from kundli.chatbot import chat as chatbot_chat
from kundli.lifeareas import generate_life_areas

app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.secret_key = os.environ.get("KUNDLI_SECRET_KEY", os.urandom(24).hex())

# Server-side chart context with TTL eviction (max 100 entries)
import time as _time

class ChartStore:
    """Simple TTL cache for chart contexts. Evicts oldest when full."""
    def __init__(self, max_size=100, ttl=3600):
        self._store = {}
        self._max_size = max_size
        self._ttl = ttl

    def set(self, key, value):
        self._evict()
        self._store[key] = {"data": value, "ts": _time.time()}

    def get(self, key):
        entry = self._store.get(key)
        if not entry:
            return None
        if _time.time() - entry["ts"] > self._ttl:
            del self._store[key]
            return None
        return entry["data"]

    def _evict(self):
        now = _time.time()
        expired = [k for k, v in self._store.items() if now - v["ts"] > self._ttl]
        for k in expired:
            del self._store[k]
        while len(self._store) >= self._max_size:
            oldest = min(self._store, key=lambda k: self._store[k]["ts"])
            del self._store[oldest]

_chart_store = ChartStore()


def get_coordinates(location):
    try:
        geo = Nominatim(user_agent="kundli_app", timeout=10)
        loc = geo.geocode(location)
        if not loc:
            return None, None
        return loc.latitude, loc.longitude
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
    return jsonify({"status": "ok"})


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
    except (ValueError, TypeError):
        return render_template("index.html", error="Invalid date or time format.")

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
    jd = to_julian(birth_dt, tz)
    planets = compute_planets(jd)
    houses = compute_houses(jd, lat, lon)
    now = datetime.now()

    # Precompute shared data once
    planet_house_map = build_planet_house_map(planets, houses)
    moon = next(p for p in planets if p["planet"] == "Chandra")
    dashas = compute_dasha(moon["longitude"], birth_dt)
    aspects = compute_aspects(planets)
    yogas = check_yogas(planets)
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

    answer = chatbot_chat(question, ctx)
    return jsonify({"answer": answer})


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG", "0") == "1", port=int(os.environ.get("PORT", 8080)))
