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
DASHA_TOTAL_YEARS = 120
ASPECTS = {
    "Surya": [7], "Chandra": [7], "Budh": [7], "Shukra": [7],
    "Mangal": [4, 7, 8], "Guru": [5, 7, 9], "Shani": [3, 7, 10],
    "Rahu": [5, 7, 9], "Ketu": [5, 7, 9],
}
EXALTATION = {
    "Surya": "Mesha", "Chandra": "Vrishabha", "Mangal": "Makara",
    "Budh": "Kanya", "Guru": "Karka", "Shukra": "Meena", "Shani": "Tula",
}
OWN_SIGNS = {
    "Mangal": ["Mesha", "Vrishchika"], "Budh": ["Mithuna", "Kanya"],
    "Guru": ["Dhanu", "Meena"], "Shukra": ["Vrishabha", "Tula"],
    "Shani": ["Makara", "Kumbha"],
}
SIGN_LORDS_CALC = {
    "Mesha": "Mangal", "Vrishabha": "Shukra", "Mithuna": "Budh", "Karka": "Chandra",
    "Simha": "Surya", "Kanya": "Budh", "Tula": "Shukra", "Vrishchika": "Mangal",
    "Dhanu": "Guru", "Makara": "Shani", "Kumbha": "Shani", "Meena": "Guru",
}

YOGAS = [
    {"name": "Gajakesari", "desc": "Guru in kendra from Chandra. Brings wisdom, fame, and prosperity",
     "check": lambda p: _in_kendra(p, "Guru", "Chandra")},
    {"name": "Budhaditya", "desc": "Surya and Budh in same sign. Brings intelligence and communication skills",
     "check": lambda p: _same_sign(p, "Surya", "Budh")},
    {"name": "Chandra-Mangal", "desc": "Chandra and Mangal in same sign. Brings wealth through enterprise",
     "check": lambda p: _same_sign(p, "Chandra", "Mangal")},
    {"name": "Sunapha", "desc": "Planet (not Sun) in 2nd from Chandra. Indicates self-made wealth",
     "check": lambda p: _has_planet_offset_from_moon(p, 1)},
    {"name": "Anapha", "desc": "Planet (not Sun) in 12th from Chandra. Indicates spiritual inclination and generosity",
     "check": lambda p: _has_planet_offset_from_moon(p, 11)},
    {"name": "Durudhura", "desc": "Planets on both sides of Chandra. Brings wealth, fame, and generous nature",
     "check": lambda p: _has_planet_offset_from_moon(p, 1) and _has_planet_offset_from_moon(p, 11)},
    {"name": "Voshi", "desc": "Planet (not Moon/Rahu/Ketu) in 12th from Surya. Indicates charitable and learned nature",
     "check": lambda p: _has_planet_offset_from_sun(p, 11)},
    {"name": "Veshi", "desc": "Planet (not Moon/Rahu/Ketu) in 2nd from Surya. Indicates eloquence and prosperity",
     "check": lambda p: _has_planet_offset_from_sun(p, 1)},
    {"name": "Obhayachari", "desc": "Planets on both sides of Surya. Indicates influential and strong personality",
     "check": lambda p: _has_planet_offset_from_sun(p, 1) and _has_planet_offset_from_sun(p, 11)},
    {"name": "Lakshmi", "desc": "Shukra in own or exalted sign. Brings wealth, beauty, and fortune",
     "check": lambda p: _get(p, "Shukra")["sign"] in ("Vrishabha", "Tula", "Meena")},
    {"name": "Chandra-Budh", "desc": "Chandra and Budh in same sign. Brings sharp mind and good memory",
     "check": lambda p: _same_sign(p, "Chandra", "Budh")},
    {"name": "Shani-Mangal", "desc": "Shani and Mangal in same sign. Brings determination and technical ability",
     "check": lambda p: _same_sign(p, "Shani", "Mangal")},
    {"name": "Surya-Mangal", "desc": "Surya and Mangal in same sign. Brings courage, leadership, and authority",
     "check": lambda p: _same_sign(p, "Surya", "Mangal")},
    {"name": "Guru-Mangal", "desc": "Guru and Mangal in same sign. Brings righteous action and spiritual courage",
     "check": lambda p: _same_sign(p, "Guru", "Mangal")},
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


def _has_planet_offset_from_moon(planets, offset):
    """Check if any planet (not Sun/Rahu/Ketu) is `offset` signs from Moon."""
    moon_idx = _sign_index(planets, "Chandra")
    target = (moon_idx + offset) % 12
    excluded = {"Surya", "Rahu", "Ketu", "Chandra"}
    return any(SIGNS.index(p["sign"]) == target for p in planets if p["planet"] not in excluded)


def _has_planet_offset_from_sun(planets, offset):
    """Check if any planet (not Moon/Rahu/Ketu) is `offset` signs from Sun."""
    sun_idx = _sign_index(planets, "Surya")
    target = (sun_idx + offset) % 12
    excluded = {"Chandra", "Rahu", "Ketu", "Surya"}
    return any(SIGNS.index(p["sign"]) == target for p in planets if p["planet"] not in excluded)


def _in_kendra_from_sign(sign1: str, sign2: str) -> bool:
    """Check if sign1 is in kendra (1/4/7/10) from sign2."""
    return (SIGNS.index(sign1) - SIGNS.index(sign2)) % 12 in (0, 3, 6, 9)


def _has_kemadruma(planets: list) -> bool:
    """Check Kemadruma. No planet (except Sun, Rahu, Ketu) adjacent to Moon."""
    moon_idx = _sign_index(planets, "Chandra")
    adjacent = {(moon_idx - 1) % 12, (moon_idx + 1) % 12}
    excluded = {"Surya", "Rahu", "Ketu", "Chandra"}
    return not any(
        SIGNS.index(p["sign"]) in adjacent for p in planets if p["planet"] not in excluded
    )


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
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        calc_result, ret_flags = swe.calc_ut(jd, pid, flags)
        lon = calc_result[0]
        lon_speed = calc_result[3]
        sid_lon = (lon - ayanamsa) % 360
        sign, deg = get_sign(sid_lon)
        nak, pada = get_nakshatra(sid_lon)
        # Rahu is always retrograde by convention, not marked
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
        "retrograde": False,  # Ketu always retrograde, conventionally not marked
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


def compute_antardasha(dashas: list[dict]) -> list[dict]:
    """Add antardasha (sub-periods) to each mahadasha."""
    for dasha in dashas:
        lord_idx = DASHA_ORDER.index(dasha["lord"])
        total_days = (dasha["end"] - dasha["start"]).total_seconds() / 86400
        sub_start = dasha["start"]
        subs = []
        for i in range(9):
            sub_lord = DASHA_ORDER[(lord_idx + i) % 9]
            sub_days = total_days * DASHA_YEARS[sub_lord] / DASHA_TOTAL_YEARS
            sub_end = sub_start + timedelta(days=sub_days)
            subs.append({"lord": sub_lord, "start": sub_start, "end": sub_end, "years": round(sub_days / 365.25, 2)})
            sub_start = sub_end
        dasha["antardasha"] = subs
    return dashas

def compute_pratyantar(dashas: list[dict]) -> list[dict]:
    """Add pratyantar (sub-sub-periods) to each antardasha."""
    for dasha in dashas:
        for ad in dasha.get("antardasha", []):
            lord_idx = DASHA_ORDER.index(ad["lord"])
            total_days = (ad["end"] - ad["start"]).total_seconds() / 86400
            sub_start = ad["start"]
            subs = []
            for i in range(9):
                sub_lord = DASHA_ORDER[(lord_idx + i) % 9]
                sub_days = total_days * DASHA_YEARS[sub_lord] / DASHA_TOTAL_YEARS
                sub_end = sub_start + timedelta(days=sub_days)
                subs.append({"lord": sub_lord, "start": sub_start, "end": sub_end, "years": round(sub_days / 365.25, 2)})
                sub_start = sub_end
            ad["pratyantar"] = subs
    return dashas


YOGINI_NAMES = ["Mangala", "Pingala", "Dhanya", "Bhramari", "Bhadrika", "Ulka", "Siddha", "Sankata"]
YOGINI_YEARS = [1, 2, 3, 4, 5, 6, 7, 8]
YOGINI_TOTAL = 36


def compute_yogini_dasha(moon_longitude: float, birth_dt) -> list[dict]:
    """Compute Yogini Dasha, a 36-year cycle with 8 yoginis."""
    nak_index = int(moon_longitude // (360 / 27))
    start_idx = (nak_index + 3) % 8
    nak_span = 360 / 27
    elapsed_frac = (moon_longitude % nak_span) / nak_span
    remaining_years = YOGINI_YEARS[start_idx] * (1 - elapsed_frac)

    dashas = []
    current = birth_dt

    # First (partial) period
    end = current + timedelta(days=remaining_years * 365.25)
    dashas.append({"lord": YOGINI_NAMES[start_idx], "start": current, "end": end, "years": round(remaining_years, 2)})
    current = end

    # Subsequent full periods, cycling through all 8 yoginis repeatedly
    i = (start_idx + 1) % 8
    while len(dashas) < 40:
        years = YOGINI_YEARS[i]
        end = current + timedelta(days=years * 365.25)
        dashas.append({"lord": YOGINI_NAMES[i], "start": current, "end": end, "years": years})
        current = end
        i = (i + 1) % 8
    return dashas


DIVISIONAL_CHARTS = {
    "D-1": {"name": "Rashi", "div": 1, "desc": "Birth chart. Overall life."},
    "D-2": {"name": "Hora", "div": 2, "desc": "Wealth and financial prosperity."},
    "D-3": {"name": "Drekkana", "div": 3, "desc": "Siblings, courage, and short journeys."},
    "D-4": {"name": "Chaturthamsa", "div": 4, "desc": "Property, fortune, and fixed assets."},
    "D-6": {"name": "Shashthamsa", "div": 6, "desc": "Health, diseases, and enemies."},
    "D-7": {"name": "Saptamsa", "div": 7, "desc": "Children and progeny."},
    "D-9": {"name": "Navamsa", "div": 9, "desc": "Marriage, dharma, and inner strength. The most important divisional chart."},
    "D-10": {"name": "Dasamsa", "div": 10, "desc": "Career, profession, and public reputation."},
    "D-12": {"name": "Dwadasamsa", "div": 12, "desc": "Parents and ancestral lineage."},
    "D-16": {"name": "Shodasamsa", "div": 16, "desc": "Vehicles, comforts, and luxuries."},
    "D-20": {"name": "Vimsamsa", "div": 20, "desc": "Spiritual progress and worship."},
    "D-24": {"name": "Chaturvimsamsa", "div": 24, "desc": "Education, learning, and knowledge."},
    "D-27": {"name": "Saptavimsamsa", "div": 27, "desc": "Physical strength and stamina."},
    "D-30": {"name": "Trimsamsa", "div": 30, "desc": "Misfortunes, challenges, and hidden difficulties."},
    "D-40": {"name": "Khavedamsa", "div": 40, "desc": "Auspicious and inauspicious effects from maternal side."},
    "D-45": {"name": "Akshavedamsa", "div": 45, "desc": "General well-being and paternal legacy."},
    "D-60": {"name": "Shashtiamsa", "div": 60, "desc": "Past-life karma. The most granular divisional chart."},
}

# D-9 Navamsa starting signs: Aries signs start from Aries, Taurus signs from Capricorn, etc.
_NAVAMSA_START = [0, 9, 6, 3, 0, 9, 6, 3, 0, 9, 6, 3]  # sign index offsets for each natal sign


def compute_divisional_chart(planets, division):
    """Compute a divisional (Varga) chart for given division number.

    For D-9 (Navamsa), uses the traditional Navamsa mapping.
    For others, uses the general formula: each sign is divided into `division` equal parts,
    and the part maps sequentially through the zodiac starting from the natal sign.
    """
    results = []
    for p in planets:
        lon = p["longitude"]
        natal_sign_idx = int(lon // 30)
        deg_in_sign = lon % 30
        part_size = 30.0 / division

        if division == 9:
            # Traditional Navamsa mapping
            part = int(deg_in_sign // part_size)
            new_sign_idx = (_NAVAMSA_START[natal_sign_idx] + part) % 12
        elif division == 2:
            # Hora: odd signs -> Sun (Leo), even signs -> Moon (Cancer)
            part = int(deg_in_sign // 15)
            if natal_sign_idx % 2 == 0:  # odd sign (0-indexed)
                new_sign_idx = 4 if part == 0 else 3  # Leo or Cancer
            else:
                new_sign_idx = 3 if part == 0 else 4
        else:
            # General formula
            part = int(deg_in_sign // part_size)
            new_sign_idx = (natal_sign_idx * division + part) % 12

        new_sign = SIGNS[new_sign_idx]
        new_deg = (deg_in_sign % part_size) * (30.0 / part_size)
        results.append({
            "planet": p["planet"],
            "sign": new_sign,
            "degree": round(new_deg, 2),
            "retrograde": p.get("retrograde", False),
        })
    return results

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

def compute_shadbala(planets: list, houses: list, planet_house_map: dict) -> list:
    """Compute simplified planetary strength (0-100 scale)."""
    lagna_sign = houses[0]["sign"]
    results = []

    # Dig Bala: directional strength based on house position
    # Each planet is strongest in a specific house
    _DIG_BEST = {"Surya": 10, "Chandra": 4, "Mangal": 10, "Budh": 1, "Guru": 1, "Shukra": 4, "Shani": 7}

    # Naisargika Bala: natural strength (fixed, descending)
    _NAISARGIKA = {"Surya": 60, "Chandra": 51, "Shukra": 43, "Guru": 34, "Budh": 26, "Mangal": 17, "Shani": 9}

    for p in planets:
        if p["planet"] in ("Rahu", "Ketu"):
            continue
        name = p["planet"]
        sign = p["sign"]
        house = planet_house_map.get(name, 1)
        score = 0

        # 1. Sthana Bala (positional): exalted=30, own=25, friend=15, neutral=10, enemy=5, debilitated=0
        if sign == EXALTATION.get(name):
            score += 30
        elif sign in OWN_SIGNS.get(name, []):
            score += 25
        else:
            score += 10  # neutral default

        # 2. Dig Bala (directional): max 25 if in best house, scaled by distance
        best = _DIG_BEST.get(name, 1)
        dist = min(abs(house - best), 12 - abs(house - best))
        score += max(0, 25 - dist * 4)

        # 3. Cheshta Bala (motional): retrograde planets get reduced strength
        if p.get("retrograde"):
            score += 5  # retrograde = some strength (revisiting)
        else:
            score += 15  # direct motion = full motional strength

        # 4. Naisargika Bala (natural): scaled to 0-30 range
        nat = _NAISARGIKA.get(name, 30)
        score += int(nat * 30 / 60)

        # Clamp to 0-100
        strength = min(100, max(0, score))
        label = "Strong" if strength >= 60 else "Moderate" if strength >= 40 else "Weak"
        results.append({"planet": name, "strength": strength, "label": label})

    results.sort(key=lambda x: x["strength"], reverse=True)
    return results



def check_doshas(planets: list, planet_house_map: dict, current_saturn_sign: str | None = None) -> list:
    """Detect doshas (afflictions) from planetary positions and house placements."""
    doshas = []

    # Manglik Dosha: Mars in 1, 2, 4, 7, 8, or 12
    mars_house = planet_house_map.get("Mangal")
    if mars_house in (1, 2, 4, 7, 8, 12):
        doshas.append({
            "name": "Manglik Dosha",
            "present": True,
            "detail": f"Mangal (Mars) is in House {mars_house}. This brings strong energy and drive. For marriage, matching with another Manglik or performing remedies can harmonize this influence.",
        })
    else:
        doshas.append({"name": "Manglik Dosha", "present": False, "detail": "Mangal is not in houses 1/2/4/7/8/12."})

    # Kalsarpa Dosha: all 7 planets (Sun-Saturn) hemmed between Rahu-Ketu axis
    rahu_lon = _get(planets, "Rahu")["longitude"]
    ketu_lon = _get(planets, "Ketu")["longitude"]
    if rahu_lon > ketu_lon:
        arc_start, arc_end = ketu_lon, rahu_lon
    else:
        arc_start, arc_end = rahu_lon, ketu_lon
    check_planets = [p for p in planets if p["planet"] not in ("Rahu", "Ketu")]
    all_in_arc = all(arc_start <= p["longitude"] <= arc_end for p in check_planets)
    all_outside = all(not (arc_start <= p["longitude"] <= arc_end) for p in check_planets)
    is_kalsarpa = all_in_arc or all_outside
    if is_kalsarpa:
        doshas.append({
            "name": "Kalsarpa Dosha",
            "present": True,
            "detail": "All planets are between the Rahu-Ketu axis. This indicates a focused karmic path. With awareness and remedies, it brings deep spiritual growth and eventual success.",
        })
    else:
        doshas.append({"name": "Kalsarpa Dosha", "present": False, "detail": "Planets are not confined to the Rahu-Ketu axis."})

    # Sade Sati: Saturn transiting 12th, 1st, or 2nd sign from natal Moon
    if current_saturn_sign:
        moon_sign_idx = SIGNS.index(_get(planets, "Chandra")["sign"])
        saturn_sign_idx = SIGNS.index(current_saturn_sign)
        diff = (saturn_sign_idx - moon_sign_idx) % 12
        if diff in (11, 0, 1):  # 12th, 1st, 2nd from Moon
            phase = {11: "Rising (12th from Moon)", 0: "Peak (over Moon)", 1: "Setting (2nd from Moon)"}[diff]
            doshas.append({
                "name": "Sade Sati",
                "present": True,
                "detail": f"Saturn is transiting {current_saturn_sign}, {phase}. This 7.5-year period builds resilience, discipline, and lasting achievements through patience.",
            })
        else:
            doshas.append({"name": "Sade Sati", "present": False, "detail": f"Saturn is in {current_saturn_sign}, not adjacent to your Moon sign."})

    return doshas


def check_yogas(planets: list, houses: list | None = None, planet_house_map: dict | None = None) -> list:
    """Detect Vedic yogas from planetary positions."""
    results = [{"name": y["name"], "desc": y["desc"]} for y in YOGAS if y["check"](planets)]

    if _has_kemadruma(planets):
        results.append({"name": "Kemadruma", "desc": "No planets adjacent to Chandra. Indicates emotional isolation and self-reliance"})

    if houses:
        lagna_sign = houses[0]["sign"]
        mahapurusha = {
            "Mangal": ("Ruchaka", "Mangal in own or exalted sign in kendra. Brings courage, leadership, and physical strength"),
            "Budh": ("Bhadra", "Budh in own or exalted sign in kendra. Brings intellect, communication, and business acumen"),
            "Guru": ("Hamsa", "Guru in own or exalted sign in kendra. Brings wisdom, spirituality, and good fortune"),
            "Shukra": ("Malavya", "Shukra in own or exalted sign in kendra. Brings beauty, luxury, and artistic talent"),
            "Shani": ("Sasa", "Shani in own or exalted sign in kendra. Brings discipline, authority, and longevity"),
        }
        for planet, (name, desc) in mahapurusha.items():
            sign = _get(planets, planet)["sign"]
            if (sign in OWN_SIGNS.get(planet, []) or sign == EXALTATION.get(planet)) \
                    and _in_kendra_from_sign(sign, lagna_sign):
                results.append({"name": name, "desc": desc})

    # House-based yogas (need planet_house_map)
    if planet_house_map and houses:
        def _lord_of_house(h_num):
            return SIGN_LORDS_CALC[houses[h_num - 1]["sign"]]

        def _house_of(planet_name):
            return planet_house_map.get(planet_name)

        # Dhana Yoga: lords of 2nd and 11th in kendra or trikona from each other
        lord2 = _lord_of_house(2)
        lord11 = _lord_of_house(11)
        h2, h11 = _house_of(lord2), _house_of(lord11)
        if h2 and h11:
            diff = (h11 - h2) % 12
            if diff in (0, 3, 4, 6, 8, 9):  # kendra or trikona
                results.append({"name": "Dhana", "desc": f"Lords of 2nd ({lord2}) and 11th ({lord11}) in mutual kendra/trikona. Brings wealth and prosperity"})

        # Raja Yoga: lord of trikona (1,5,9) conjunct lord of kendra (1,4,7,10)
        trikona_lords = {_lord_of_house(h) for h in (1, 5, 9)}
        kendra_lords = {_lord_of_house(h) for h in (1, 4, 7, 10)}
        for tl in trikona_lords:
            for kl in kendra_lords:
                if tl != kl and _house_of(tl) == _house_of(kl) and _house_of(tl) is not None:
                    results.append({"name": "Raja", "desc": f"{tl} (trikona lord) conjunct {kl} (kendra lord) in House {_house_of(tl)}. Brings power and authority"})
                    break
            else:
                continue
            break

        # Viparita Raja: lords of 6th, 8th, or 12th in each other's houses
        dusthana = {6, 8, 12}
        for h in dusthana:
            lord = _lord_of_house(h)
            lord_h = _house_of(lord)
            if lord_h in dusthana and lord_h != h:
                results.append({"name": "Viparita Raja", "desc": f"Lord of {h}th ({lord}) in {lord_h}th house. Indicates success through adversity"})
                break

        # Adhi Yoga: benefics (Guru, Shukra, Budh) in 6th, 7th, 8th from Moon
        moon_sign_idx = SIGNS.index(_get(planets, "Chandra")["sign"])
        benefic_houses = {(moon_sign_idx + offset) % 12 for offset in (5, 6, 7)}  # 6th, 7th, 8th
        benefics_in = sum(1 for p in planets if p["planet"] in ("Guru", "Shukra", "Budh") and SIGNS.index(p["sign"]) in benefic_houses)
        if benefics_in >= 2:
            results.append({"name": "Adhi", "desc": "Benefics in 6/7/8th from Chandra. Brings leadership, authority, and prosperity"})

        # Amala Yoga: benefic in 10th from Lagna or Moon
        lagna_idx = SIGNS.index(houses[0]["sign"])
        tenth_from_lagna = (lagna_idx + 9) % 12
        tenth_from_moon = (moon_sign_idx + 9) % 12
        for p in planets:
            if p["planet"] in ("Guru", "Shukra", "Budh") and SIGNS.index(p["sign"]) in (tenth_from_lagna, tenth_from_moon):
                results.append({"name": "Amala", "desc": f"{p['planet']} in 10th. Brings lasting fame and virtuous reputation"})
                break

    return results
