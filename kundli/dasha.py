"""Vimshottari and Yogini Dasha calculations."""
from datetime import timedelta

from kundli.core import NAKSHATRA_LORDS

DASHA_YEARS = {
    "Ketu": 7, "Shukra": 20, "Surya": 6, "Chandra": 10, "Mangal": 7,
    "Rahu": 18, "Guru": 16, "Shani": 19, "Budh": 17,
}
DASHA_ORDER = ["Ketu", "Shukra", "Surya", "Chandra", "Mangal", "Rahu", "Guru", "Shani", "Budh"]
DASHA_TOTAL_YEARS = 120

YOGINI_NAMES = ["Mangala", "Pingala", "Dhanya", "Bhramari", "Bhadrika", "Ulka", "Siddha", "Sankata"]
YOGINI_YEARS = [1, 2, 3, 4, 5, 6, 7, 8]
YOGINI_TOTAL = 36


def compute_dasha(moon_longitude, birth_dt):
    """Compute Vimshottari Mahadasha periods from Moon longitude."""
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


def compute_yogini_dasha(moon_longitude: float, birth_dt) -> list[dict]:
    """Compute Yogini Dasha, a 36-year cycle with 8 yoginis."""
    nak_index = int(moon_longitude // (360 / 27))
    start_idx = (nak_index + 3) % 8
    nak_span = 360 / 27
    elapsed_frac = (moon_longitude % nak_span) / nak_span
    remaining_years = YOGINI_YEARS[start_idx] * (1 - elapsed_frac)

    dashas = []
    current = birth_dt

    end = current + timedelta(days=remaining_years * 365.25)
    dashas.append({"lord": YOGINI_NAMES[start_idx], "start": current, "end": end, "years": round(remaining_years, 2)})
    current = end

    i = (start_idx + 1) % 8
    while len(dashas) < 40:
        years = YOGINI_YEARS[i]
        end = current + timedelta(days=years * 365.25)
        dashas.append({"lord": YOGINI_NAMES[i], "start": current, "end": end, "years": years})
        current = end
        i = (i + 1) % 8
    return dashas
