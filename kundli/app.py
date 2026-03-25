"""CLI application for Kundli generation."""
import argparse
from datetime import datetime, timedelta, timezone
from geopy.geocoders import Nominatim

from kundli.calc import (
    to_julian, compute_planets, compute_houses,
    compute_dasha, compute_antardasha, compute_pratyantar,
    compute_aspects, check_yogas, check_doshas,
    build_planet_house_map,
)
from kundli.chart import draw_north_indian, draw_south_indian
from kundli.readings import build_house_readings
from kundli.match import compute_ashtakoota


def get_coordinates(location):
    geo = Nominatim(user_agent="kundli_app", timeout=10)
    loc = geo.geocode(location)
    if not loc:
        raise ValueError(f"Could not find location: {location}")
    return loc.latitude, loc.longitude


def print_section(title):
    print(f"\n  -- {title} {'─' * (50 - len(title))}")


def _get_moon_info(date_str, time_str, location, tz):
    """Parse inputs and return moon nakshatra info."""
    day, month, year = map(int, date_str.split("-"))
    hour, minute = map(int, time_str.split(":"))
    birth_dt = datetime(year, month, day, hour, minute)
    lat, lon = get_coordinates(location)
    jd = to_julian(birth_dt, tz)
    planets = compute_planets(jd)
    moon = next(p for p in planets if p["planet"] == "Chandra")
    nak_idx = int(moon["longitude"] // (360 / 27))
    return {"sign": moon["sign"], "nakshatra": moon["nakshatra"], "nak_idx": nak_idx}


def run_match(args):
    """Run Ashtakoota Gun Milan match."""
    m1 = _get_moon_info(args.date, args.time, args.location, args.tz)
    m2 = _get_moon_info(args.date2, args.time2, args.location2, args.tz2)
    result = compute_ashtakoota(m1["nak_idx"], m2["nak_idx"])

    print(f"\n{'=' * 60}")
    print(f"  KUNDLI MATCH -- Ashtakoota Gun Milan")
    print(f"{'=' * 60}")
    print(f"  Person 1: {m1['sign']} / {m1['nakshatra']}")
    print(f"  Person 2: {m2['sign']} / {m2['nakshatra']}")
    print(f"\n  {'Koota':<16} {'Person 1':<14} {'Person 2':<14} {'Score':>7}")
    print(f"  {'-' * 55}")
    for k in result["kootas"]:
        print(f"  {k['name']:<16} {k['boy']:<14} {k['girl']:<14} {k['score']:>4}/{k['max']}")
    print(f"  {'-' * 55}")
    print(f"  {'Total':<16} {'':<14} {'':<14} {result['total']:>4}/{result['max']}")

    pct = result["total"] / result["max"] * 100
    if result["total"] >= 32:
        verdict = "Excellent match"
    elif result["total"] >= 24:
        verdict = "Good match, recommended"
    elif result["total"] >= 18:
        verdict = "Average, proceed with caution"
    else:
        verdict = "Not recommended"
    print(f"\n  Verdict: {verdict} ({pct:.0f}%)")

    nadi = result["kootas"][7]
    bhakoot = result["kootas"][6]
    if nadi["score"] == 0:
        print(f"\n  ⚠ Nadi Dosha: Both have {nadi['boy']} Nadi")
    if bhakoot["score"] == 0:
        print(f"  ⚠ Bhakoot Dosha: {bhakoot['boy']}-{bhakoot['girl']} axis")
    print(f"\n{'=' * 60}\n")


def main():
    parser = argparse.ArgumentParser(description="Vedic Kundli (Birth Chart) Generator")
    parser.add_argument("--date", required=True, help="Birth date: DD-MM-YYYY")
    parser.add_argument("--time", required=True, help="Birth time: HH:MM (24h)")
    parser.add_argument("--location", required=True, help="Birth place")
    parser.add_argument("--tz", type=float, default=5.5, help="Timezone offset from UTC (default: 5.5 for IST)")
    parser.add_argument("--chart", choices=["north", "south", "both"], default="both", help="Chart style")
    parser.add_argument("--match", action="store_true", help="Match mode: compare two charts")
    parser.add_argument("--date2", help="Second person birth date: DD-MM-YYYY (match mode)")
    parser.add_argument("--time2", help="Second person birth time: HH:MM (match mode)")
    parser.add_argument("--location2", help="Second person birth place (match mode)")
    parser.add_argument("--tz2", type=float, default=5.5, help="Second person timezone offset (match mode)")
    args = parser.parse_args()

    if args.match:
        if not all([args.date2, args.time2, args.location2]):
            parser.error("--match requires --date2, --time2, --location2")
        return run_match(args)

    day, month, year = map(int, args.date.split("-"))
    hour, minute = map(int, args.time.split(":"))
    birth_dt = datetime(year, month, day, hour, minute)

    lat, lon = get_coordinates(args.location)
    jd = to_julian(birth_dt, args.tz)
    planets = compute_planets(jd)
    houses = compute_houses(jd, lat, lon)
    now = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=args.tz)
    planet_house_map = build_planet_house_map(planets, houses)
    moon = next(p for p in planets if p["planet"] == "Chandra")
    dashas = compute_dasha(moon["longitude"], birth_dt)
    dashas = compute_antardasha(dashas)
    dashas = compute_pratyantar(dashas)

    # Header
    print(f"\n{'=' * 60}")
    print(f"  KUNDLI -- Vedic Birth Chart")
    print(f"{'=' * 60}")
    print(f"  Date  : {birth_dt.strftime('%d %B %Y, %I:%M %p')}")
    print(f"  Place : {args.location} ({lat:.4f}, {lon:.4f})")
    print(f"  Lagna : {houses[0]['sign']} {houses[0]['degree']:.2f}")

    # Planets
    print_section("Planetary Positions")
    print(f"  {'Planet':<10} {'Sign':<13} {'Deg':>7}  {'Nakshatra':<20} Pada")
    print(f"  {'-' * 60}")
    for p in planets:
        print(f"  {p['planet']:<10} {p['sign']:<13} {p['degree']:>6.2f}"
              f"  {p['nakshatra']:<20} {p['pada']}")

    # Houses
    print_section("House Cusps")
    for h in houses:
        marker = " <- Asc" if h["house"] == 1 else ""
        print(f"  House {h['house']:>2}: {h['sign']:<13} {h['degree']:>6.2f}{marker}")

    # Charts
    if args.chart in ("north", "both"):
        print_section("North Indian Chart")
        print(draw_north_indian(planets, houses))
    if args.chart in ("south", "both"):
        print_section("South Indian Chart")
        print(draw_south_indian(planets))

    # Aspects
    print_section("Planetary Aspects")
    aspects = compute_aspects(planets)
    if aspects:
        for a in aspects:
            targets = ", ".join(a["to"])
            print(f"  {a['from']:<10} aspects {targets} (in {a['target_sign']})")
    else:
        print("  No direct planetary aspects found.")

    # Yogas
    print_section("Yogas")
    yogas = check_yogas(planets, houses, planet_house_map)
    if yogas:
        for y in yogas:
            print(f"  * {y['name']}: {y['desc']}")
    else:
        print("  No major yogas detected.")

    # Doshas
    print_section("Doshas")
    current_jd = to_julian(now, 0)
    current_planets = compute_planets(current_jd)
    current_saturn_sign = next(p["sign"] for p in current_planets if p["planet"] == "Shani")
    doshas = check_doshas(planets, planet_house_map, current_saturn_sign)
    for d in doshas:
        status = "⚠ YES" if d["present"] else "✓ No"
        print(f"  {d['name']:<20} {status}")
        print(f"    {d['detail']}")

    # Vimshottari Dasha
    print_section("Vimshottari Dasha")
    for d in dashas:
        md_active = d["start"] <= now <= d["end"]
        marker = " << CURRENT" if md_active else ""
        print(f"  {d['lord']:<10} {d['start'].strftime('%d-%b-%Y')} -> "
              f"{d['end'].strftime('%d-%b-%Y')}  ({d['years']} yrs){marker}")
        if md_active:
            for ad in d.get("antardasha", []):
                ad_active = ad["start"] <= now <= ad["end"]
                ad_marker = " << CURRENT" if ad_active else ""
                print(f"    {ad['lord']:<10} {ad['start'].strftime('%d-%b-%Y')} -> "
                      f"{ad['end'].strftime('%d-%b-%Y')}  ({ad['years']} yrs){ad_marker}")
                if ad_active:
                    for pr in ad.get("pratyantar", []):
                        pr_active = pr["start"] <= now <= pr["end"]
                        pr_marker = " << CURRENT" if pr_active else ""
                        print(f"      {pr['lord']:<10} {pr['start'].strftime('%d-%b-%Y')} -> "
                              f"{pr['end'].strftime('%d-%b-%Y')}  ({pr['years']} yrs){pr_marker}")

    # House Readings
    print_section("House Readings")
    readings, current_dasha = build_house_readings(planets, houses, dashas, now, planet_house_map)
    if current_dasha:
        print(f"\n  Current Mahadasha: {current_dasha}\n")
    for r in readings:
        print(f"  {'-' * 56}")
        print(f"  House {r['num']}: {r['theme']}")
        print(f"    {r['sign']} | Lord: {r['lord']} (House {r['lord_house']})")
        if r['occupants']:
            print(f"    Planets: {', '.join(r['occupants'])}")
            for pr in r['planet_readings']:
                if pr['reading']:
                    print(f"      {pr['name']}: {pr['reading']}")
        if r['aspectors']:
            print(f"    Aspected by: {', '.join(r['aspectors'])}")
        if r['lord_note']:
            print(f"    Lord {r['lord']} {r['lord_note']}")
        if r['dasha_note']:
            print(f"    * ACTIVE: {current_dasha} {r['dasha_note']}")
    print(f"  {'-' * 56}")

    print(f"\n{'=' * 60}\n")


if __name__ == "__main__":
    main()
