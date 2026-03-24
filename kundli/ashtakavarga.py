"""Ashtakavarga — point-based transit prediction system."""

# Benefic points: for each planet, which houses (from each contributing planet/lagna) give a point.
# Key = planet being evaluated, Value = dict of contributor -> list of favorable houses (1-indexed from contributor)
# Source: standard Parashari Ashtakavarga tables

_BAV_RULES = {
    "Surya": {
        "Surya": [1, 2, 4, 7, 8, 9, 10, 11],
        "Chandra": [3, 6, 10, 11],
        "Mangal": [1, 2, 4, 7, 8, 9, 10, 11],
        "Budh": [3, 5, 6, 9, 10, 11, 12],
        "Guru": [5, 6, 9, 11],
        "Shukra": [6, 7, 12],
        "Shani": [1, 2, 4, 7, 8, 9, 10, 11],
        "Lagna": [3, 4, 6, 10, 11, 12],
    },
    "Chandra": {
        "Surya": [3, 6, 7, 8, 10, 11],
        "Chandra": [1, 3, 6, 7, 10, 11],
        "Mangal": [2, 3, 5, 6, 9, 10, 11],
        "Budh": [1, 3, 4, 5, 7, 8, 10, 11],
        "Guru": [1, 4, 7, 8, 10, 11, 12],
        "Shukra": [3, 4, 5, 7, 9, 10, 11],
        "Shani": [3, 5, 6, 11],
        "Lagna": [3, 6, 10, 11],
    },
    "Mangal": {
        "Surya": [3, 5, 6, 10, 11],
        "Chandra": [3, 6, 11],
        "Mangal": [1, 2, 4, 7, 8, 10, 11],
        "Budh": [3, 5, 6, 11],
        "Guru": [6, 10, 11, 12],
        "Shukra": [6, 8, 11, 12],
        "Shani": [1, 4, 7, 8, 9, 10, 11],
        "Lagna": [1, 3, 6, 10, 11],
    },
    "Budh": {
        "Surya": [5, 6, 9, 11, 12],
        "Chandra": [2, 4, 6, 8, 10, 11],
        "Mangal": [1, 2, 4, 7, 8, 9, 10, 11],
        "Budh": [1, 3, 5, 6, 9, 10, 11, 12],
        "Guru": [6, 8, 11, 12],
        "Shukra": [1, 2, 3, 4, 5, 8, 9, 11],
        "Shani": [1, 2, 4, 7, 8, 9, 10, 11],
        "Lagna": [1, 2, 4, 6, 8, 10, 11],
    },
    "Guru": {
        "Surya": [1, 2, 3, 4, 7, 8, 9, 10, 11],
        "Chandra": [2, 5, 7, 9, 11],
        "Mangal": [1, 2, 4, 7, 8, 10, 11],
        "Budh": [1, 2, 4, 5, 6, 9, 10, 11],
        "Guru": [1, 2, 3, 4, 7, 8, 10, 11],
        "Shukra": [2, 5, 6, 9, 10, 11],
        "Shani": [3, 5, 6, 12],
        "Lagna": [1, 2, 4, 5, 6, 7, 9, 10, 11],
    },
    "Shukra": {
        "Surya": [8, 11, 12],
        "Chandra": [1, 2, 3, 4, 5, 8, 9, 11, 12],
        "Mangal": [3, 5, 6, 9, 11, 12],
        "Budh": [3, 5, 6, 9, 11],
        "Guru": [5, 8, 9, 10, 11],
        "Shukra": [1, 2, 3, 4, 5, 8, 9, 10, 11],
        "Shani": [3, 4, 5, 8, 9, 10, 11],
        "Lagna": [1, 2, 3, 4, 5, 8, 9, 11],
    },
    "Shani": {
        "Surya": [1, 2, 4, 7, 8, 10, 11],
        "Chandra": [3, 6, 11],
        "Mangal": [3, 5, 6, 10, 11, 12],
        "Budh": [6, 8, 9, 10, 11, 12],
        "Guru": [5, 6, 11, 12],
        "Shukra": [6, 11, 12],
        "Shani": [3, 5, 6, 11],
        "Lagna": [1, 3, 4, 6, 10, 11],
    },
}

SIGNS = [
    "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
    "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena",
]


def compute_ashtakavarga(planets: list, houses: list) -> dict:
    """Compute Bhinnashtakavarga (per-planet) and Sarvashtakavarga (total).

    Returns:
        Dict with 'bav' (per-planet 12-sign point arrays) and 'sav' (total 12-sign array).
    """
    # Build sign index lookup for planets and lagna
    positions = {}
    for p in planets:
        if p["planet"] in _BAV_RULES:
            positions[p["planet"]] = SIGNS.index(p["sign"])
    positions["Lagna"] = SIGNS.index(houses[0]["sign"])

    bav = {}
    sav = [0] * 12

    for planet, rules in _BAV_RULES.items():
        points = [0] * 12
        for contributor, favorable_houses in rules.items():
            if contributor not in positions:
                continue
            contrib_sign_idx = positions[contributor]
            for h in favorable_houses:
                target_sign = (contrib_sign_idx + h - 1) % 12
                points[target_sign] += 1
        bav[planet] = points
        for i in range(12):
            sav[i] += points[i]

    return {"bav": bav, "sav": sav, "signs": SIGNS}
