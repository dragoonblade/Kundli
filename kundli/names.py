"""Name translation maps and astrological reference data."""

PLANET_NAMES = {
    "Surya": "Sun", "Chandra": "Moon", "Mangal": "Mars",
    "Budh": "Mercury", "Guru": "Jupiter", "Shukra": "Venus",
    "Shani": "Saturn", "Rahu": "Rahu", "Ketu": "Ketu",
}

SIGN_NAMES = {
    "Mesha": "Aries", "Vrishabha": "Taurus", "Mithuna": "Gemini",
    "Karka": "Cancer", "Simha": "Leo", "Kanya": "Virgo",
    "Tula": "Libra", "Vrishchika": "Scorpio", "Dhanu": "Sagittarius",
    "Makara": "Capricorn", "Kumbha": "Aquarius", "Meena": "Pisces",
}

SIGN_LORDS = {
    "Mesha": "Mangal", "Vrishabha": "Shukra", "Mithuna": "Budh", "Karka": "Chandra",
    "Simha": "Surya", "Kanya": "Budh", "Tula": "Shukra", "Vrishchika": "Mangal",
    "Dhanu": "Guru", "Makara": "Shani", "Kumbha": "Shani", "Meena": "Guru",
}

PLANET_ABBR = {
    "hindu": {"Surya": "Su", "Chandra": "Ch", "Mangal": "Ma", "Budh": "Bu",
              "Guru": "Gu", "Shukra": "Sk", "Shani": "Sa", "Rahu": "Ra", "Ketu": "Ke"},
    "english": {"Surya": "Su", "Chandra": "Mo", "Mangal": "Ma", "Budh": "Me",
                "Guru": "Ju", "Shukra": "Ve", "Shani": "Sa", "Rahu": "Ra", "Ketu": "Ke"},
}

SIGN_ABBR = {
    "hindu": {s: s[:3] for s in SIGN_NAMES},
    "english": {s: e[:3] for s, e in SIGN_NAMES.items()},
}
