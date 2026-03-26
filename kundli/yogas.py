"""Yoga detection from planetary positions."""
from kundli.core import SIGNS, EXALTATION, OWN_SIGNS, SIGN_LORDS_CALC, _get, _sign_index

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


def _in_kendra(planets, p1, p2):
    """Check if p1 is in kendra (1/4/7/10) from p2."""
    diff = (_sign_index(planets, p1) - _sign_index(planets, p2)) % 12
    return diff in [0, 3, 6, 9]


def _same_sign(planets, p1, p2):
    """Check if two planets are in the same sign."""
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

    if planet_house_map and houses:
        def _lord_of_house(h_num):
            return SIGN_LORDS_CALC[houses[h_num - 1]["sign"]]

        def _house_of(planet_name):
            return planet_house_map.get(planet_name)

        lord2 = _lord_of_house(2)
        lord11 = _lord_of_house(11)
        h2, h11 = _house_of(lord2), _house_of(lord11)
        if h2 and h11:
            diff = (h11 - h2) % 12
            if diff in (0, 3, 4, 6, 8, 9):
                results.append({"name": "Dhana", "desc": f"Lords of 2nd ({lord2}) and 11th ({lord11}) in mutual kendra/trikona. Brings wealth and prosperity"})

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

        dusthana = {6, 8, 12}
        for h in dusthana:
            lord = _lord_of_house(h)
            lord_h = _house_of(lord)
            if lord_h in dusthana and lord_h != h:
                results.append({"name": "Viparita Raja", "desc": f"Lord of {h}th ({lord}) in {lord_h}th house. Indicates success through adversity"})
                break

        moon_sign_idx = SIGNS.index(_get(planets, "Chandra")["sign"])
        benefic_houses = {(moon_sign_idx + offset) % 12 for offset in (5, 6, 7)}
        benefics_in = sum(1 for p in planets if p["planet"] in ("Guru", "Shukra", "Budh") and SIGNS.index(p["sign"]) in benefic_houses)
        if benefics_in >= 2:
            results.append({"name": "Adhi", "desc": "Benefics in 6/7/8th from Chandra. Brings leadership, authority, and prosperity"})

        lagna_idx = SIGNS.index(houses[0]["sign"])
        tenth_from_lagna = (lagna_idx + 9) % 12
        tenth_from_moon = (moon_sign_idx + 9) % 12
        for p in planets:
            if p["planet"] in ("Guru", "Shukra", "Budh") and SIGNS.index(p["sign"]) in (tenth_from_lagna, tenth_from_moon):
                results.append({"name": "Amala", "desc": f"{p['planet']} in 10th. Brings lasting fame and virtuous reputation"})
                break

    return results
