"""Shadbala (planetary strength) calculation."""
from kundli.core import EXALTATION, OWN_SIGNS


def compute_shadbala(planets: list, houses: list, planet_house_map: dict) -> list:
    """Compute simplified planetary strength (0-100 scale)."""
    _DIG_BEST = {"Surya": 10, "Chandra": 4, "Mangal": 10, "Budh": 1, "Guru": 1, "Shukra": 4, "Shani": 7}
    _NAISARGIKA = {"Surya": 60, "Chandra": 51, "Shukra": 43, "Guru": 34, "Budh": 26, "Mangal": 17, "Shani": 9}

    results = []
    for p in planets:
        if p["planet"] in ("Rahu", "Ketu"):
            continue
        name = p["planet"]
        sign = p["sign"]
        house = planet_house_map.get(name, 1)
        score = 0

        # 1. Sthana Bala (positional)
        if sign == EXALTATION.get(name):
            score += 30
        elif sign in OWN_SIGNS.get(name, []):
            score += 25
        else:
            score += 10

        # 2. Dig Bala (directional)
        best = _DIG_BEST.get(name, 1)
        dist = min(abs(house - best), 12 - abs(house - best))
        score += max(0, 25 - dist * 4)

        # 3. Cheshta Bala (motional)
        score += 5 if p.get("retrograde") else 15

        # 4. Naisargika Bala (natural)
        nat = _NAISARGIKA.get(name, 30)
        score += int(nat * 30 / 60)

        strength = min(100, max(0, score))
        label = "Strong" if strength >= 60 else "Moderate" if strength >= 40 else "Weak"
        results.append({"planet": name, "strength": strength, "label": label})

    results.sort(key=lambda x: x["strength"], reverse=True)
    return results
