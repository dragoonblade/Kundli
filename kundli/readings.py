"""House-by-house readings based on sign, lord, and occupying planets."""
import json
import os

from kundli.calc import SIGNS
from kundli.names import SIGN_LORDS

_DATA_PATH = os.path.join(os.path.dirname(__file__), "readings_data.json")
with open(_DATA_PATH) as _f:
    _DATA = json.load(_f)

HOUSE_THEMES = {int(k): tuple(v) for k, v in _DATA["HOUSE_THEMES"].items()}
PLANET_IN_HOUSE = {p: {int(h): txt for h, txt in houses.items()} for p, houses in _DATA["PLANET_IN_HOUSE"].items()}
SIMPLE_PLANET_IN_HOUSE = {p: {int(h): txt for h, txt in houses.items()} for p, houses in _DATA["SIMPLE_PLANET_IN_HOUSE"].items()}
HOUSE_SIMPLE = {int(k): v for k, v in _DATA["HOUSE_SIMPLE"].items()}
DASHA_EFFECTS = _DATA["DASHA_EFFECTS"]
SIMPLE_DASHA_EFFECTS = _DATA["SIMPLE_DASHA_EFFECTS"]
DASHA_HOUSE_INFLUENCE = {p: {int(h): txt for h, txt in houses.items()} for p, houses in _DATA["DASHA_HOUSE_INFLUENCE"].items()}
RETROGRADE_EFFECTS = _DATA["RETROGRADE_EFFECTS"]


def build_house_readings(planets, houses, dashas, now, planet_house_map=None):
    """Build structured house readings for both general and advanced modes.

    Args:
        planets: list of planet dicts from compute_planets
        houses: list of house dicts from compute_houses
        dashas: list of dasha dicts from compute_dasha
        now: datetime for current dasha detection
        planet_house_map: precomputed {planet_name: house_num}, built if not provided

    Returns:
        (readings_list, current_dasha_lord)
    """
    from kundli.calc import build_planet_house_map, get_aspecting_planets

    if planet_house_map is None:
        planet_house_map = build_planet_house_map(planets, houses)

    current_dasha = None
    for d in dashas:
        if d["start"] <= now <= d["end"]:
            current_dasha = d["lord"]
            break

    def occupants(hnum):
        return [p for p in planets if planet_house_map.get(p["planet"]) == hnum]

    readings = []
    for h in houses:
        num = h["house"]
        sign = h["sign"]
        lord = SIGN_LORDS[sign]
        theme, keywords = HOUSE_THEMES[num]
        occ = occupants(num)
        aspectors = get_aspecting_planets(planets, sign)
        lord_house = planet_house_map.get(lord)

        # Advanced planet readings
        planet_readings = []
        simple_planet_readings = []
        for o in occ:
            retro = o.get("retrograde", False)
            retro_text = RETROGRADE_EFFECTS.get(o["planet"], {}).get("general", "") if retro else ""
            retro_simple = RETROGRADE_EFFECTS.get(o["planet"], {}).get("simple", "") if retro else ""
            planet_readings.append({
                "name": o["planet"],
                "reading": PLANET_IN_HOUSE.get(o["planet"], {}).get(num, ""),
                "retrograde": retro,
                "retrograde_text": retro_text,
            })
            simple_planet_readings.append({
                "name": o["planet"],
                "reading": SIMPLE_PLANET_IN_HOUSE.get(o["planet"], {}).get(num, ""),
                "retrograde": retro,
                "retrograde_text": retro_simple,
            })

        # Lord note
        lord_note = ""
        if lord_house:
            if lord_house == num:
                lord_note = f"in own house, strengthening all {theme.lower()} matters"
            else:
                lh_theme = HOUSE_THEMES[lord_house][0]
                lord_note = f"in House {lord_house} ({lh_theme}), connecting {theme.lower()} with {lh_theme.lower()}"

        # Dasha notes
        dasha_note = ""
        simple_dasha_note = ""
        current_influence = ""
        if current_dasha:
            dasha_house = planet_house_map.get(current_dasha)
            dasha_effect = DASHA_EFFECTS.get(current_dasha, "")
            simple_effect = SIMPLE_DASHA_EFFECTS.get(current_dasha, "")
            current_influence = DASHA_HOUSE_INFLUENCE.get(current_dasha, {}).get(num, "")
            if dasha_house == num:
                dasha_note = f"Dasha lord sits here, so this house is currently activated ({dasha_effect})"
                simple_dasha_note = f"This area of your life is especially active right now. It's {simple_effect}."
            elif current_dasha == lord:
                dasha_note = f"Dasha is the lord of this house, expect developments in {keywords}"
                simple_dasha_note = "You may notice changes here soon. The current period brings focus to this area."
            elif current_dasha in aspectors:
                dasha_note = f"Dasha lord aspects this house, bringing indirect influence on {theme.lower()}"
                simple_dasha_note = "This area is getting some extra attention during this period of your life."

        # General summary
        simple_summary = HOUSE_SIMPLE[num]
        if occ:
            extras = [SIMPLE_PLANET_IN_HOUSE.get(o["planet"], {}).get(num, "") for o in occ]
            simple_summary += " " + " ".join(s for s in extras if s)

        readings.append({
            "num": num, "sign": sign, "lord": lord, "lord_house": lord_house,
            "theme": theme, "keywords": keywords,
            "occupants": [o["planet"] for o in occ],
            "planet_readings": planet_readings,
            "simple_planet_readings": simple_planet_readings,
            "aspectors": aspectors, "lord_note": lord_note, "dasha_note": dasha_note,
            "simple_summary": simple_summary, "simple_dasha_note": simple_dasha_note,
            "current_influence": current_influence,
        })
    return readings, current_dasha
