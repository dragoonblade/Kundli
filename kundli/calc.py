"""Core astronomical calculations for Kundli."""
import swisseph as swe
from datetime import datetime, timedelta

PLANETS = {
    swe.SUN: "Surya", swe.MOON: "Chandra", swe.MARS: "Mangal",
    swe.MERCURY: "Budh", swe.JUPITER: "Guru", swe.VENUS: "Shukra",
    swe.SATURN: "Shani", swe.MEAN_NODE: "Rahu",
}
SIGNS = [
    "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
    "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena",
]
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]
NAKSHATRA_LORDS = [
    "Ketu", "Shukra", "Surya", "Chandra", "Mangal", "Rahu",
    "Guru", "Shani", "Budh",
]
DASHA_YEARS = {
    "Ketu": 7, "Shukra": 20, "Surya": 6, "Chandra": 10, "Mangal": 7,
    "Rahu": 18, "Guru": 16, "Shani": 19, "Budh": 17,
}
DASHA_ORDER = ["Ketu", "Shukra", "Surya", "Chandra", "Mangal", "Rahu", "Guru", "Shani", "Budh"]
ASPECTS = {
    "Surya": [7], "Chandra": [7], "Budh": [7], "Shukra": [7],
    "Mangal": [4, 7, 8], "Guru": [5, 7, 9], "Shani": [3, 7, 10],
    "Rahu": [5, 7, 9], "Ketu": [5, 7, 9],
}
YOGAS = [
    {"name": "Gajakesari", "desc": "Guru in kendra from Chandra",
     "check": lambda p: _in_kendra(p, "Guru", "Chandra")},
    {"name": "Budhaditya", "desc": "Surya and Budh in same sign",
     "check": lambda p: _same_sign(p, "Surya", "Budh")},
    {"name": "Chandra-Mangal", "desc": "Chandra and Mangal in same sign",
     "check": lambda p: _same_sign(p, "Chandra", "Mangal")},
]


def _get(planets, name):
    return next(p for p in planets if p["planet"] == name)


def _sign_index(planets, name):
    return SIGNS.index(_get(planets, name)["sign"])


def _in_kendra(planets, p1, p2):
    diff = (_sign_index(planets, p1) - _sign_index(planets, p2)) % 12
    return diff in [0, 3, 6, 9]


def _same_sign(planets, p1, p2):
    return _get(planets, p1)["sign"] == _get(planets, p2)["sign"]


def get_sign(longitude):
    index = int(longitude // 30)
    return SIGNS[index], longitude % 30


def get_nakshatra(longitude):
    span = 360 / 27
    index = int(longitude // span)
    pada = int((longitude % span) // (span / 4)) + 1
    return NAKSHATRAS[index], pada


def to_julian(dt, tz_offset):
    ut_hour = dt.hour + dt.minute / 60.0 + dt.second / 3600.0 - tz_offset
    return swe.julday(dt.year, dt.month, dt.day, ut_hour)


# Initialize ephemeris and sidereal mode once at import time
swe.set_ephe_path(None)
swe.set_sid_mode(swe.SIDM_LAHIRI)


def compute_planets(jd):
    ayanamsa = swe.get_ayanamsa_ut(jd)
    results = []
    for pid, name in PLANETS.items():
        lon = swe.calc_ut(jd, pid)[0][0]
        sid_lon = (lon - ayanamsa) % 360
        sign, deg = get_sign(sid_lon)
        nak, pada = get_nakshatra(sid_lon)
        results.append({
            "planet": name, "longitude": round(sid_lon, 4),
            "sign": sign, "degree": round(deg, 2),
            "nakshatra": nak, "pada": pada,
        })
    rahu_lon = _get(results, "Rahu")["longitude"]
    ketu_lon = (rahu_lon + 180) % 360
    sign, deg = get_sign(ketu_lon)
    nak, pada = get_nakshatra(ketu_lon)
    results.append({
        "planet": "Ketu", "longitude": round(ketu_lon, 4),
        "sign": sign, "degree": round(deg, 2),
        "nakshatra": nak, "pada": pada,
    })
    return results


def compute_houses(jd, lat, lon):
    ayanamsa = swe.get_ayanamsa_ut(jd)
    cusps, _ = swe.houses(jd, lat, lon, b'P')
    houses = []
    for i, cusp in enumerate(cusps, 1):
        sid_cusp = (cusp - ayanamsa) % 360
        sign, deg = get_sign(sid_cusp)
        houses.append({"house": i, "sign": sign, "degree": round(deg, 2)})
    return houses


def compute_dasha(moon_longitude, birth_dt):
    nak_index = int(moon_longitude // (360 / 27))
    lord = NAKSHATRA_LORDS[nak_index % 9]
    nak_span = 360 / 27
    elapsed_in_nak = (moon_longitude % nak_span) / nak_span
    remaining_years = DASHA_YEARS[lord] * (1 - elapsed_in_nak)

    start_idx = DASHA_ORDER.index(lord)
    dashas = []
    current = birth_dt

    days = remaining_years * 365.25
    end = current + timedelta(days=days)
    dashas.append({"lord": lord, "start": current, "end": end, "years": round(remaining_years, 2)})
    current = end

    for i in range(1, 9):
        idx = (start_idx + i) % 9
        lord = DASHA_ORDER[idx]
        years = DASHA_YEARS[lord]
        end = current + timedelta(days=years * 365.25)
        dashas.append({"lord": lord, "start": current, "end": end, "years": years})
        current = end

    return dashas



def build_planet_house_map(planets, houses):
    """Precompute which house each planet occupies. Returns {planet_name: house_num}."""
    mapping = {}
    for p in planets:
        p_lon = p["longitude"]
        assigned = houses[0]["house"]
        for i in range(12):
            cusp_start = SIGNS.index(houses[i]["sign"]) * 30 + houses[i]["degree"]
            next_i = (i + 1) % 12
            cusp_end = SIGNS.index(houses[next_i]["sign"]) * 30 + houses[next_i]["degree"]
            if cusp_end <= cusp_start:
                cusp_end += 360
            test_lon = p_lon if p_lon >= cusp_start else p_lon + 360
            if cusp_start <= test_lon < cusp_end:
                assigned = houses[i]["house"]
                break
        mapping[p["planet"]] = assigned
    return mapping


def get_aspecting_planets(planets, house_sign):
    """Find planets aspecting a given sign."""
    target_idx = SIGNS.index(house_sign)
    aspecting = []
    for p in planets:
        p_idx = SIGNS.index(p["sign"])
        for h in ASPECTS.get(p["planet"], [7]):
            if (p_idx + h - 1) % 12 == target_idx:
                aspecting.append(p["planet"])
                break
    return aspecting

def compute_aspects(planets):
    results = []
    for p in planets:
        p_sign_idx = SIGNS.index(p["sign"])
        aspect_houses = ASPECTS.get(p["planet"], [7])
        for h in aspect_houses:
            target_sign = SIGNS[(p_sign_idx + h - 1) % 12]
            aspected = [o["planet"] for o in planets
                        if o["sign"] == target_sign and o["planet"] != p["planet"]]
            if aspected:
                results.append({
                    "from": p["planet"], "to": aspected,
                    "aspect_house": h, "target_sign": target_sign,
                })
    return results


def check_yogas(planets):
    return [{"name": y["name"], "desc": y["desc"]}
            for y in YOGAS if y["check"](planets)]
