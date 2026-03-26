"""Constants and helpers shared across all Kundli modules."""
import swisseph as swe

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

# Initialize ephemeris and sidereal mode once at import time
swe.set_ephe_path(None)
swe.set_sid_mode(swe.SIDM_LAHIRI)


def get_sign(longitude):
    """Return (sign_name, degree_within_sign) for a sidereal longitude."""
    index = int(longitude // 30)
    return SIGNS[index], longitude % 30


def get_nakshatra(longitude):
    """Return (nakshatra_name, pada) for a sidereal longitude."""
    span = 360 / 27
    index = int(longitude // span)
    pada = int((longitude % span) // (span / 4)) + 1
    return NAKSHATRAS[index], pada


def to_julian(dt, tz_offset):
    """Convert a datetime and timezone offset to Julian Day number."""
    ut_hour = dt.hour + dt.minute / 60.0 + dt.second / 3600.0 - tz_offset
    return swe.julday(dt.year, dt.month, dt.day, ut_hour)


def _get(planets, name):
    """Get a planet dict by name from a planets list."""
    return next(p for p in planets if p["planet"] == name)


def _sign_index(planets, name):
    """Get the sign index (0-11) for a named planet."""
    return SIGNS.index(_get(planets, name)["sign"])
