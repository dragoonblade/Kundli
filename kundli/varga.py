"""Divisional (Varga) chart calculations."""
from kundli.core import SIGNS

DIVISIONAL_CHARTS = {
    "D-1": {"name": "Rashi", "div": 1, "desc": "Birth chart. Overall life."},
    "D-2": {"name": "Hora", "div": 2, "desc": "Wealth and financial prosperity."},
    "D-3": {"name": "Drekkana", "div": 3, "desc": "Siblings, courage, and short journeys."},
    "D-4": {"name": "Chaturthamsa", "div": 4, "desc": "Property, fortune, and fixed assets."},
    "D-6": {"name": "Shashthamsa", "div": 6, "desc": "Health, diseases, and enemies."},
    "D-7": {"name": "Saptamsa", "div": 7, "desc": "Children and progeny."},
    "D-9": {"name": "Navamsa", "div": 9, "desc": "Marriage, dharma, and inner strength. The most important divisional chart."},
    "D-10": {"name": "Dasamsa", "div": 10, "desc": "Career, profession, and public reputation."},
    "D-12": {"name": "Dwadasamsa", "div": 12, "desc": "Parents and ancestral lineage."},
    "D-16": {"name": "Shodasamsa", "div": 16, "desc": "Vehicles, comforts, and luxuries."},
    "D-20": {"name": "Vimsamsa", "div": 20, "desc": "Spiritual progress and worship."},
    "D-24": {"name": "Chaturvimsamsa", "div": 24, "desc": "Education, learning, and knowledge."},
    "D-27": {"name": "Saptavimsamsa", "div": 27, "desc": "Physical strength and stamina."},
    "D-30": {"name": "Trimsamsa", "div": 30, "desc": "Misfortunes, challenges, and hidden difficulties."},
    "D-40": {"name": "Khavedamsa", "div": 40, "desc": "Auspicious and inauspicious effects from maternal side."},
    "D-45": {"name": "Akshavedamsa", "div": 45, "desc": "General well-being and paternal legacy."},
    "D-60": {"name": "Shashtiamsa", "div": 60, "desc": "Past-life karma. The most granular divisional chart."},
}

_NAVAMSA_START = [0, 9, 6, 3, 0, 9, 6, 3, 0, 9, 6, 3]


def compute_divisional_chart(planets, division):
    """Compute a divisional (Varga) chart for given division number.

    For D-9 (Navamsa), uses the traditional Navamsa mapping.
    For D-2 (Hora), uses Sun/Moon (Leo/Cancer) mapping.
    For others, uses the general formula.
    """
    results = []
    for p in planets:
        lon = p["longitude"]
        natal_sign_idx = int(lon // 30)
        deg_in_sign = lon % 30
        part_size = 30.0 / division

        if division == 9:
            part = int(deg_in_sign // part_size)
            new_sign_idx = (_NAVAMSA_START[natal_sign_idx] + part) % 12
        elif division == 2:
            part = int(deg_in_sign // 15)
            if natal_sign_idx % 2 == 0:
                new_sign_idx = 4 if part == 0 else 3
            else:
                new_sign_idx = 3 if part == 0 else 4
        else:
            part = int(deg_in_sign // part_size)
            new_sign_idx = (natal_sign_idx * division + part) % 12

        new_sign = SIGNS[new_sign_idx]
        new_deg = (deg_in_sign % part_size) * (30.0 / part_size)
        results.append({
            "planet": p["planet"],
            "sign": new_sign,
            "degree": round(new_deg, 2),
            "retrograde": p.get("retrograde", False),
        })
    return results
