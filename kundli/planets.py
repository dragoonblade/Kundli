"""Planetary positions, house cusps, aspects, and planet-house mapping."""
import swisseph as swe

from kundli.core import PLANETS, SIGNS, ASPECTS, get_sign, get_nakshatra, _get


def compute_planets(jd):
    """Compute sidereal positions of all 9 Navagraha for a Julian Day."""
    ayanamsa = swe.get_ayanamsa_ut(jd)
    results = []
    for pid, name in PLANETS.items():
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        calc_result, ret_flags = swe.calc_ut(jd, pid, flags)
        lon = calc_result[0]
        lon_speed = calc_result[3]
        sid_lon = (lon - ayanamsa) % 360
        sign, deg = get_sign(sid_lon)
        nak, pada = get_nakshatra(sid_lon)
        retrograde = lon_speed < 0 and name != "Rahu"
        results.append({
            "planet": name, "longitude": round(sid_lon, 4),
            "sign": sign, "degree": round(deg, 2),
            "nakshatra": nak, "pada": pada,
            "retrograde": retrograde,
        })
    rahu_lon = _get(results, "Rahu")["longitude"]
    ketu_lon = (rahu_lon + 180) % 360
    sign, deg = get_sign(ketu_lon)
    nak, pada = get_nakshatra(ketu_lon)
    results.append({
        "planet": "Ketu", "longitude": round(ketu_lon, 4),
        "sign": sign, "degree": round(deg, 2),
        "nakshatra": nak, "pada": pada,
        "retrograde": False,
    })
    return results


def compute_houses(jd, lat, lon):
    """Compute 12 house cusps using Placidus system."""
    ayanamsa = swe.get_ayanamsa_ut(jd)
    cusps, _ = swe.houses(jd, lat, lon, b'P')
    houses = []
    for i, cusp in enumerate(cusps, 1):
        sid_cusp = (cusp - ayanamsa) % 360
        sign, deg = get_sign(sid_cusp)
        houses.append({"house": i, "sign": sign, "degree": round(deg, 2)})
    return houses


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
    """Compute Vedic planetary aspects between all planets."""
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
