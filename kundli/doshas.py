"""Dosha detection: Manglik, Kalsarpa, Sade Sati."""
from kundli.core import SIGNS, _get


def check_doshas(planets: list, planet_house_map: dict, current_saturn_sign: str | None = None) -> list:
    """Detect doshas (afflictions) from planetary positions and house placements."""
    doshas = []

    # Manglik Dosha
    mars_house = planet_house_map.get("Mangal")
    if mars_house in (1, 2, 4, 7, 8, 12):
        doshas.append({
            "name": "Manglik Dosha",
            "present": True,
            "detail": f"Mangal (Mars) is in House {mars_house}. This brings strong energy and drive. For marriage, matching with another Manglik or performing remedies can harmonize this influence.",
        })
    else:
        doshas.append({"name": "Manglik Dosha", "present": False, "detail": "Mangal is not in houses 1/2/4/7/8/12."})

    # Kalsarpa Dosha
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

    # Sade Sati
    if current_saturn_sign:
        moon_sign_idx = SIGNS.index(_get(planets, "Chandra")["sign"])
        saturn_sign_idx = SIGNS.index(current_saturn_sign)
        diff = (saturn_sign_idx - moon_sign_idx) % 12
        if diff in (11, 0, 1):
            phase = {11: "Rising (12th from Moon)", 0: "Peak (over Moon)", 1: "Setting (2nd from Moon)"}[diff]
            doshas.append({
                "name": "Sade Sati",
                "present": True,
                "detail": f"Saturn is transiting {current_saturn_sign}, {phase}. This 7.5-year period builds resilience, discipline, and lasting achievements through patience.",
            })
        else:
            doshas.append({"name": "Sade Sati", "present": False, "detail": f"Saturn is in {current_saturn_sign}, not adjacent to your Moon sign."})

    return doshas
