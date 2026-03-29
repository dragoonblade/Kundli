"""Event Predictor: favorable dasha periods for major life events."""
from datetime import datetime, timedelta, timezone

from kundli.core import SIGN_LORDS_CALC

# Life events mapped to relevant houses and natural significators
EVENT_CONFIG = {
    "marriage": {"houses": [7], "planets": ["Shukra", "Guru"], "icon": "💍", "label": "Marriage"},
    "children": {"houses": [5], "planets": ["Guru"], "icon": "👶", "label": "Children"},
    "career": {"houses": [10], "planets": ["Surya", "Shani"], "icon": "💼", "label": "Career Growth"},
    "wealth": {"houses": [2, 11], "planets": ["Guru", "Shukra"], "icon": "💰", "label": "Wealth"},
    "education": {"houses": [5, 9], "planets": ["Budh", "Guru"], "icon": "🎓", "label": "Education"},
    "travel": {"houses": [9, 12], "planets": ["Rahu"], "icon": "✈️", "label": "Foreign Travel"},
}


def compute_event_periods(dashas: list, houses: list, tz_offset: float = 5.5) -> list:
    """Compute favorable dasha periods for major life events.

    Returns a list of event dicts, each with past and future favorable windows.
    """
    now = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=tz_offset)
    results = []

    for key, cfg in EVENT_CONFIG.items():
        # Collect house lords + natural significators
        relevant = set(cfg["planets"])
        for h in cfg["houses"]:
            relevant.add(SIGN_LORDS_CALC[houses[h - 1]["sign"]])

        past, future = [], []
        for d in dashas:
            if d["lord"] not in relevant:
                continue
            entry = {"lord": d["lord"], "start": d["start"], "end": d["end"], "level": "MD"}
            if d["end"] < now:
                past.append(entry)
            elif d["start"] > now:
                future.append(entry)
            else:
                future.insert(0, entry)  # current period first

        # Also scan antardashas for more granular timing
        for d in dashas:
            for ad in d.get("antardasha", []):
                if ad["lord"] not in relevant or d["lord"] in relevant:
                    continue  # skip if MD already counted
                entry = {"lord": ad["lord"], "start": ad["start"], "end": ad["end"], "level": "AD"}
                if ad["end"] < now:
                    past.append(entry)
                elif ad["start"] > now and len(future) < 6:
                    future.append(entry)
                elif ad["start"] <= now <= ad["end"]:
                    future.insert(0, entry)

        past.sort(key=lambda x: x["start"], reverse=True)
        results.append({
            "key": key,
            "label": cfg["label"],
            "icon": cfg["icon"],
            "lords": sorted(relevant),
            "past": past[:3],
            "future": future[:4],
            "active": any(f["start"] <= now <= f["end"] for f in future),
        })

    return results
