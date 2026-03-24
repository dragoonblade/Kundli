"""Ashtakoota (8 Koota) Gun Milan compatibility scoring for Vedic astrology."""

_VARNA_NAMES = ["Shudra", "Vaishya", "Kshatriya", "Brahmin"]
_VARNA_BY_SIGN = [2, 1, 0, 3, 2, 1, 0, 3, 2, 1, 0, 3]

_VASHYA_NAMES = ["Chatushpada", "Manava", "Jalachara", "Vanachara", "Keeta"]
_VASHYA_GROUP = [0, 0, 1, 2, 3, 1, 1, 4, 1, 0, 1, 2]
_VASHYA_SCORE = [
    [2, 1, 1, 0, 1],
    [1, 2, 1, 1, 0],
    [1, 1, 2, 1, 1],
    [0, 1, 1, 2, 1],
    [1, 0, 1, 1, 2],
]

_YONI_NAMES = ["Horse", "Elephant", "Sheep", "Serpent", "Dog", "Cat", "Rat", "Cow", "Buffalo", "Tiger", "Hare", "Monkey", "Mongoose", "Lion"]
_YONI_ANIMAL = [0, 1, 2, 3, 3, 4, 5, 2, 5, 6, 6, 7, 8, 9, 8, 9, 10, 10, 4, 11, 12, 11, 13, 0, 13, 7, 1]
_YONI_ENEMIES = {frozenset(p) for p in [(5, 6), (7, 9), (0, 8), (4, 10), (3, 12), (2, 11), (1, 13)]}

_GANA_NAMES = ["Deva", "Manushya", "Rakshasa"]
_GANA = [0, 1, 2, 1, 0, 1, 0, 0, 2, 2, 1, 0, 0, 2, 0, 2, 0, 2, 2, 1, 1, 0, 2, 2, 1, 1, 0]
_GANA_SCORE = [[6, 5, 1], [3, 6, 0], [1, 0, 6]]

_NADI_NAMES = ["Aadi", "Madhya", "Antya"]
_NADI = [0, 1, 2, 2, 1, 0, 0, 1, 2, 2, 1, 0, 0, 1, 2, 2, 1, 0, 0, 1, 2, 2, 1, 0, 0, 1, 2]

_SIGN_LORD = ["Mangal", "Shukra", "Budh", "Chandra", "Surya", "Budh", "Shukra", "Mangal", "Guru", "Shani", "Shani", "Guru"]
_SIGN_NAMES = ["Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya", "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena"]

_GRAHA_FRIENDS = {
    "Surya":   {"friend": {"Chandra", "Mangal", "Guru"}, "enemy": {"Shukra", "Shani"}},
    "Chandra": {"friend": {"Surya", "Budh"}, "enemy": set()},
    "Mangal":  {"friend": {"Surya", "Chandra", "Guru"}, "enemy": {"Budh"}},
    "Budh":    {"friend": {"Surya", "Shukra"}, "enemy": {"Chandra"}},
    "Guru":    {"friend": {"Surya", "Chandra", "Mangal"}, "enemy": {"Budh", "Shukra"}},
    "Shukra":  {"friend": {"Budh", "Shani"}, "enemy": {"Surya", "Chandra"}},
    "Shani":   {"friend": {"Budh", "Shukra"}, "enemy": {"Surya", "Chandra", "Mangal"}},
}

_BHAKOOT_BAD = {1, 4, 5, 7, 8, 11}


def _sign_of(nak_idx: int) -> int:
    return int(nak_idx * 4 / 9)


def _relationship(lord1: str, lord2: str) -> int:
    """Return 1=friend, 0=neutral, -1=enemy."""
    if lord2 in _GRAHA_FRIENDS[lord1]["friend"]:
        return 1
    if lord2 in _GRAHA_FRIENDS[lord1]["enemy"]:
        return -1
    return 0


def compute_ashtakoota(nak1_idx: int, nak2_idx: int) -> dict:
    """Compute Ashtakoota compatibility between two nakshatras.

    Args:
        nak1_idx: Nakshatra index (0-26) of person 1 (boy).
        nak2_idx: Nakshatra index (0-26) of person 2 (girl).

    Returns:
        Dict with 'kootas' (list of 8 koota results), 'total' (score), 'max' (36).
    """
    sign1, sign2 = _sign_of(nak1_idx), _sign_of(nak2_idx)
    kootas = []

    # 1. Varna
    v1, v2 = _VARNA_BY_SIGN[sign1], _VARNA_BY_SIGN[sign2]
    kootas.append({
        "name": "Varna", "description": "Spiritual compatibility", "max": 1,
        "score": 1 if v1 >= v2 else 0, "boy": _VARNA_NAMES[v1], "girl": _VARNA_NAMES[v2],
    })

    # 2. Vashya
    g1, g2 = _VASHYA_GROUP[sign1], _VASHYA_GROUP[sign2]
    kootas.append({
        "name": "Vashya", "description": "Dominance compatibility", "max": 2,
        "score": _VASHYA_SCORE[g1][g2], "boy": _VASHYA_NAMES[g1], "girl": _VASHYA_NAMES[g2],
    })

    # 3. Tara
    tara_boy = (nak2_idx - nak1_idx) % 9
    tara_girl = (nak1_idx - nak2_idx) % 9
    score_tara = (1.5 if tara_boy % 2 == 0 else 0) + (1.5 if tara_girl % 2 == 0 else 0)
    kootas.append({
        "name": "Tara", "description": "Destiny compatibility", "max": 3,
        "score": score_tara, "boy": str(tara_boy), "girl": str(tara_girl),
    })

    # 4. Yoni
    a1, a2 = _YONI_ANIMAL[nak1_idx], _YONI_ANIMAL[nak2_idx]
    if a1 == a2:
        ys = 4
    elif frozenset({a1, a2}) in _YONI_ENEMIES:
        ys = 0
    else:
        ys = 2
    kootas.append({
        "name": "Yoni", "description": "Physical compatibility", "max": 4,
        "score": ys, "boy": _YONI_NAMES[a1], "girl": _YONI_NAMES[a2],
    })

    # 5. Graha Maitri
    lord1, lord2 = _SIGN_LORD[sign1], _SIGN_LORD[sign2]
    if lord1 == lord2:
        gm = 5
    else:
        total_r = _relationship(lord1, lord2) + _relationship(lord2, lord1)
        gm = {2: 5, 1: 4, 0: 3, -1: 1, -2: 0}[total_r]
    kootas.append({
        "name": "Graha Maitri", "description": "Planetary friendship", "max": 5,
        "score": gm, "boy": lord1, "girl": lord2,
    })

    # 6. Gana
    ga1, ga2 = _GANA[nak1_idx], _GANA[nak2_idx]
    kootas.append({
        "name": "Gana", "description": "Temperament compatibility", "max": 6,
        "score": _GANA_SCORE[ga1][ga2], "boy": _GANA_NAMES[ga1], "girl": _GANA_NAMES[ga2],
    })

    # 7. Bhakoot
    diff = (sign2 - sign1) % 12
    kootas.append({
        "name": "Bhakoot", "description": "Health and wealth compatibility", "max": 7,
        "score": 0 if diff in _BHAKOOT_BAD else 7, "boy": _SIGN_NAMES[sign1], "girl": _SIGN_NAMES[sign2],
    })

    # 8. Nadi
    n1, n2 = _NADI[nak1_idx], _NADI[nak2_idx]
    kootas.append({
        "name": "Nadi", "description": "Health and genetic compatibility", "max": 8,
        "score": 0 if n1 == n2 else 8, "boy": _NADI_NAMES[n1], "girl": _NADI_NAMES[n2],
    })

    return {"kootas": kootas, "total": sum(k["score"] for k in kootas), "max": 36}
