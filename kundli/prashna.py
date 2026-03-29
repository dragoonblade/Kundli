"""Prashna Kundli (Horary) analysis for yes/no questions."""
from kundli.core import SIGNS, SIGN_LORDS_CALC, EXALTATION, OWN_SIGNS, _get
from kundli.planets import get_aspecting_planets

CATEGORIES = {
    "career": {"label": "Career/Job", "houses": [10, 6], "icon": "💼"},
    "education": {"label": "Education/Exams", "houses": [5, 4, 9], "icon": "🎓"},
    "relationship": {"label": "Relationships/Marriage", "houses": [7, 5], "icon": "💑"},
    "breakup": {"label": "Breakup/Reconciliation", "houses": [7, 5, 12], "icon": "💔"},
    "finance": {"label": "Finance/Wealth", "houses": [2, 11, 8], "icon": "💰"},
    "business": {"label": "Business", "houses": [7, 10, 11], "icon": "🏢"},
    "children": {"label": "Pregnancy/Children", "houses": [5, 1, 9], "icon": "👶"},
    "health": {"label": "Health/Recovery", "houses": [1, 6, 8], "icon": "🏥"},
    "travel": {"label": "Travel/Relocation", "houses": [3, 9, 12], "icon": "✈️"},
    "legal": {"label": "Legal/Disputes", "houses": [6, 7], "icon": "⚖️"},
    "lost": {"label": "Lost/Missing", "houses": [2, 4, 7], "icon": "🔍"},
    "general": {"label": "General Timing", "houses": [1, 9], "icon": "🕐"},
}


def _planet_dignity(planet_name: str, sign: str) -> str:
    """Check if a planet is exalted, in own sign, or neutral."""
    if sign == EXALTATION.get(planet_name):
        return "exalted"
    if sign in OWN_SIGNS.get(planet_name, []):
        return "own_sign"
    return "neutral"


def analyze_prashna(planets: list, houses: list, category: str) -> dict:
    """Analyze a Prashna chart for a given question category.

    Returns dict with indicators, overall tendency, and details.
    """
    cfg = CATEGORIES.get(category, CATEGORIES["general"])
    lagna_sign = houses[0]["sign"]
    lagna_lord = SIGN_LORDS_CALC[lagna_sign]
    moon = _get(planets, "Chandra")

    favorable, unfavorable = [], []

    # 1. Lagna lord strength
    ll = _get(planets, lagna_lord)
    ll_dignity = _planet_dignity(lagna_lord, ll["sign"])
    if ll_dignity == "exalted":
        favorable.append(f"Lagna lord {lagna_lord} is exalted in {ll['sign']}, a strong positive indicator")
    elif ll_dignity == "own_sign":
        favorable.append(f"Lagna lord {lagna_lord} is in own sign {ll['sign']}, showing strength")
    elif ll["retrograde"]:
        unfavorable.append(f"Lagna lord {lagna_lord} is retrograde, suggesting delays or reconsideration")

    # 2. Moon placement
    moon_dignity = _planet_dignity("Chandra", moon["sign"])
    if moon_dignity in ("exalted", "own_sign"):
        favorable.append(f"Moon is strong in {moon['sign']}, supporting a positive outcome")
    moon_sign_idx = SIGNS.index(moon["sign"])
    if moon_sign_idx in (3, 5, 7):  # Karka, Kanya, Vrishchika (waning positions)
        unfavorable.append("Moon is in a challenging sign, suggesting emotional uncertainty")

    # 3. Relevant house analysis
    for h_num in cfg["houses"]:
        h_sign = houses[h_num - 1]["sign"]
        h_lord = SIGN_LORDS_CALC[h_sign]
        h_lord_planet = _get(planets, h_lord)
        h_lord_dignity = _planet_dignity(h_lord, h_lord_planet["sign"])

        # House lord strength
        if h_lord_dignity == "exalted":
            favorable.append(f"House {h_num} lord {h_lord} is exalted, strongly supporting this matter")
        elif h_lord_dignity == "own_sign":
            favorable.append(f"House {h_num} lord {h_lord} is in own sign, a good indicator")

        # Planets in the house
        occupants = [p for p in planets if p["sign"] == h_sign]
        for occ in occupants:
            if occ["planet"] in ("Guru", "Shukra"):
                favorable.append(f"{occ['planet']} in House {h_num} ({h_sign}) brings blessings to this area")
            elif occ["planet"] in ("Shani", "Rahu", "Ketu") and occ["planet"] != h_lord:
                unfavorable.append(f"{occ['planet']} in House {h_num} may bring obstacles or delays")

        # Benefic aspects
        aspectors = get_aspecting_planets(planets, h_sign)
        if "Guru" in aspectors:
            favorable.append(f"Jupiter aspects House {h_num}, a protective and favorable influence")

    # Overall tendency
    score = len(favorable) - len(unfavorable)
    if score >= 2:
        tendency = "favorable"
        summary = "Indicators suggest favorable conditions for this matter."
    elif score <= -1:
        tendency = "challenging"
        summary = "Indicators suggest some challenges. Patience and careful planning are advised."
    else:
        tendency = "mixed"
        summary = "Indicators are mixed. The outcome may depend on timing and effort."

    return {
        "category": cfg["label"],
        "icon": cfg["icon"],
        "lagna": lagna_sign,
        "lagna_lord": lagna_lord,
        "moon_sign": moon["sign"],
        "favorable": favorable[:5],
        "unfavorable": unfavorable[:4],
        "tendency": tendency,
        "summary": summary,
    }
