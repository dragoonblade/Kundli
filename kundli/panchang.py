"""Daily Panchang: Tithi, Nakshatra, Yoga, Karana, Paksha from Moon and Sun positions."""
from kundli.core import NAKSHATRAS, get_sign
from kundli.planets import compute_planets

TITHI_NAMES = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya",
]

YOGA_NAMES = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana",
    "Atiganda", "Sukarma", "Dhriti", "Shula", "Ganda",
    "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
    "Siddhi", "Vyatipata", "Variyan", "Parigha", "Shiva",
    "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma",
    "Indra", "Vaidhriti",
]

KARANA_NAMES = [
    "Bava", "Balava", "Kaulava", "Taitila", "Garaja",
    "Vanija", "Vishti", "Shakuni", "Chatushpada", "Naga", "Kimstughna",
]

# Inauspicious yogas (traditionally avoided for new ventures)
_INAUSPICIOUS_YOGAS = {"Vishkambha", "Atiganda", "Shula", "Ganda", "Vyaghata", "Vajra", "Vyatipata", "Parigha", "Vaidhriti"}


def compute_panchang(jd: float) -> dict:
    """Compute Panchang elements for a given Julian Day.

    Returns dict with tithi, paksha, nakshatra, yoga, karana, moon_sign, auspicious.
    """
    planets = compute_planets(jd)
    sun_lon = next(p["longitude"] for p in planets if p["planet"] == "Surya")
    moon_lon = next(p["longitude"] for p in planets if p["planet"] == "Chandra")

    # Tithi: each 12 degrees of Moon-Sun separation
    diff = (moon_lon - sun_lon) % 360
    tithi_index = min(int(diff / 12), 29)
    tithi = TITHI_NAMES[tithi_index]
    paksha = "Shukla (Waxing)" if tithi_index < 15 else "Krishna (Waning)"

    # Nakshatra: Moon's current nakshatra
    nak_index = int(moon_lon // (360 / 27))
    nakshatra = NAKSHATRAS[nak_index]

    # Yoga: (Sun + Moon longitude) / (360/27)
    yoga_index = int(((sun_lon + moon_lon) % 360) / (360 / 27))
    yoga = YOGA_NAMES[yoga_index % 27]

    # Karana: half-tithi
    karana_index = int(diff / 6) % 11
    karana = KARANA_NAMES[karana_index]

    # Moon sign
    moon_sign, _ = get_sign(moon_lon)

    # Auspiciousness
    if yoga in _INAUSPICIOUS_YOGAS:
        auspicious = "caution"
        auspicious_text = f"{yoga} yoga today. Take a mindful, careful approach."
    elif tithi in ("Purnima", "Ekadashi") and yoga not in _INAUSPICIOUS_YOGAS:
        auspicious = "good"
        auspicious_text = f"{tithi} is considered auspicious. A good day for important decisions."
    elif tithi == "Amavasya":
        auspicious = "neutral"
        auspicious_text = "Amavasya (New Moon). A day for reflection and inner work."
    else:
        auspicious = "good"
        auspicious_text = "Generally favorable conditions today."

    return {
        "tithi": tithi,
        "tithi_num": (tithi_index % 15) + 1,
        "paksha": paksha,
        "nakshatra": nakshatra,
        "yoga": yoga,
        "karana": karana,
        "moon_sign": moon_sign,
        "auspicious": auspicious,
        "auspicious_text": auspicious_text,
    }
