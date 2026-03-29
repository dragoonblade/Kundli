"""Deep life area readings combining multiple houses into cohesive narratives."""
from kundli.calc import build_planet_house_map, get_aspecting_planets
from kundli.readings import (
    HOUSE_THEMES, SIMPLE_PLANET_IN_HOUSE,
    DASHA_HOUSE_INFLUENCE,
)
from kundli.names import PLANET_NAMES, SIGN_LORDS

LIFE_AREAS = [
    {
        "id": "career", "icon": "💼", "title": "Career & Profession",
        "houses": [10, 6, 2],
        "key_planets": ["Surya", "Shani", "Budh", "Guru"],
        "desc": "Your professional life, reputation, daily work, and earning potential",
    },
    {
        "id": "love", "icon": "💑", "title": "Love & Marriage",
        "houses": [7, 5],
        "key_planets": ["Shukra", "Guru", "Mangal", "Chandra"],
        "desc": "Romantic relationships, marriage, partnerships, and compatibility",
    },
    {
        "id": "wealth", "icon": "💰", "title": "Wealth & Finances",
        "houses": [2, 11, 8],
        "key_planets": ["Guru", "Shukra", "Shani", "Budh"],
        "desc": "Income, savings, investments, gains, and financial growth",
    },
    {
        "id": "health", "icon": "🏥", "title": "Health & Wellness",
        "houses": [1, 6, 8],
        "key_planets": ["Surya", "Mangal", "Shani", "Chandra"],
        "desc": "Physical health, vitality, chronic conditions, and mental well-being",
    },
    {
        "id": "education", "icon": "🎓", "title": "Education & Intellect",
        "houses": [4, 5, 9],
        "key_planets": ["Budh", "Guru", "Surya"],
        "desc": "Learning, academic success, higher education, and intellectual growth",
    },
    {
        "id": "travel", "icon": "✈️", "title": "Travel & Foreign",
        "houses": [9, 12, 3],
        "key_planets": ["Rahu", "Ketu", "Guru", "Chandra"],
        "desc": "Foreign travel, immigration, overseas career, and cultural experiences",
    },
    {
        "id": "spiritual", "icon": "🙏", "title": "Spirituality & Inner Growth",
        "houses": [9, 12, 8],
        "key_planets": ["Ketu", "Guru", "Shani", "Chandra"],
        "desc": "Spiritual path, meditation, past-life karma, and inner transformation",
    },
    {
        "id": "family", "icon": "👨‍👩‍👧", "title": "Family & Home",
        "houses": [4, 2, 5],
        "key_planets": ["Chandra", "Surya", "Guru", "Shukra"],
        "desc": "Parents, children, home life, property, and domestic happiness",
    },
]

# Narrative templates for planet placement relevance to each area
AREA_PLANET_CONTEXT = {
    "career": {
        "Surya": "gives you natural authority and leadership ability in your profession",
        "Shani": "brings discipline and persistence, you rise slowly but build a lasting career",
        "Budh": "makes you skilled in communication, technology, or business",
        "Guru": "brings wisdom and respect, suited for advisory, teaching, or legal roles",
        "Mangal": "gives you drive and ambition, great for engineering, sports, or military",
        "Shukra": "draws you toward creative, artistic, or luxury-related careers",
        "Chandra": "makes you popular and suited for public-facing or nurturing roles",
        "Rahu": "pushes you toward unconventional or foreign career paths",
        "Ketu": "may detach you from career ambition, favoring spiritual or healing work",
    },
    "love": {
        "Shukra": "is the planet of love, its placement strongly shapes your romantic life",
        "Guru": "brings wisdom and commitment to relationships",
        "Mangal": "adds passion and intensity but can also bring conflicts",
        "Chandra": "makes you emotionally invested in relationships",
        "Surya": "can make you or your partner dominant in the relationship",
        "Shani": "may delay marriage but brings a mature, lasting bond",
        "Rahu": "may attract unconventional or foreign partners",
        "Ketu": "brings karmic, past-life connections in relationships",
        "Budh": "makes communication key in your relationships",
    },
    "wealth": {
        "Guru": "is the greatest wealth-giver, brings abundance through wisdom",
        "Shukra": "attracts wealth through luxury, arts, or beauty",
        "Shani": "builds wealth slowly through hard work and discipline",
        "Budh": "brings wealth through intellect, business, or trade",
        "Surya": "can bring wealth through government or authority",
        "Mangal": "earns through courage, competition, or property",
        "Chandra": "brings fluctuating finances tied to public dealings",
        "Rahu": "can bring sudden or unconventional wealth",
        "Ketu": "may create detachment from material wealth",
    },
    "health": {
        "Surya": "governs vitality and overall life force",
        "Mangal": "rules physical energy, blood, and accidents",
        "Shani": "relates to chronic conditions, bones, and aging",
        "Chandra": "governs mental health, emotions, and fluids",
        "Rahu": "can bring mysterious or hard-to-diagnose conditions",
        "Ketu": "relates to spiritual health and sudden ailments",
        "Guru": "generally protects health and promotes healing",
        "Shukra": "relates to reproductive health and kidneys",
        "Budh": "governs nervous system and skin",
    },
    "education": {
        "Budh": "is the planet of intellect, sharpens learning and analytical ability",
        "Guru": "brings deep wisdom, higher education, and teaching ability",
        "Surya": "gives focus and clarity in studies",
        "Chandra": "adds imagination and creative intelligence",
        "Shani": "requires discipline but gives deep, thorough understanding",
        "Rahu": "may draw you to unconventional or foreign education",
        "Ketu": "gives intuitive knowledge and spiritual intelligence",
        "Mangal": "adds competitive edge in exams and technical subjects",
        "Shukra": "draws you toward arts, music, or design education",
    },
    "travel": {
        "Rahu": "is the strongest indicator of foreign travel and settlement",
        "Ketu": "may bring spiritual pilgrimages or unexpected relocations",
        "Guru": "favors travel for education, teaching, or spiritual growth",
        "Chandra": "brings emotional connections to foreign places",
        "Shani": "may bring long stays abroad, often for work",
        "Surya": "can bring government or authority-related travel",
        "Mangal": "brings adventurous or work-related travel",
        "Budh": "favors travel for business, trade, or education",
        "Shukra": "brings pleasurable travel and luxury experiences abroad",
    },
    "spiritual": {
        "Ketu": "is the planet of liberation, its placement defines your spiritual path",
        "Guru": "brings wisdom, dharma, and connection to a guru",
        "Shani": "teaches through discipline, karma, and patience",
        "Chandra": "adds emotional depth to your spiritual journey",
        "Surya": "connects you to your soul's purpose and dharma",
        "Rahu": "may create spiritual confusion before eventual awakening",
        "Mangal": "adds energy and determination to spiritual practice",
        "Budh": "brings intellectual approach to spirituality",
        "Shukra": "adds devotion and artistic expression to spiritual life",
    },
    "family": {
        "Chandra": "governs your emotional bonds and relationship with mother",
        "Surya": "shapes your relationship with father and authority at home",
        "Guru": "brings blessings, children, and family harmony",
        "Shukra": "adds comfort, beauty, and love to home life",
        "Shani": "may bring responsibilities or delays in family matters",
        "Mangal": "can bring energy but also conflicts at home",
        "Budh": "creates an intellectual family environment",
        "Rahu": "may bring unconventional family dynamics",
        "Ketu": "may create detachment from family or hometown",
    },
}


def generate_life_areas(planets, houses, dashas, current_dasha, planet_house_map=None):
    """Generate deep readings for each life area."""
    if planet_house_map is None:
        planet_house_map = build_planet_house_map(planets, houses)

    def _occupants(hnum):
        return [p for p in planets if planet_house_map.get(p["planet"]) == hnum]

    def _planet_house(name):
        return planet_house_map.get(name)
    results = []

    for area in LIFE_AREAS:
        sections = []

        # 1. Overview from relevant houses
        overview_parts = []
        for hnum in area["houses"]:
            occupants = _occupants(hnum)
            theme = HOUSE_THEMES[hnum][0]
            sign = houses[hnum - 1]["sign"]
            lord = SIGN_LORDS[sign]
            lord_house = planet_house_map.get(lord)

            if occupants:
                for o in occupants:
                    reading = SIMPLE_PLANET_IN_HOUSE.get(o["planet"], {}).get(hnum, "")
                    if reading:
                        overview_parts.append(reading)
            else:
                if lord_house:
                    lh_theme = HOUSE_THEMES[lord_house][0]
                    en_lord = PLANET_NAMES.get(lord, lord)
                    overview_parts.append(
                        f"Your {theme.lower()} area is ruled by {lord} ({en_lord}), "
                        f"placed in your {lh_theme.lower()} house, linking these two areas of life."
                    )

        if overview_parts:
            sections.append({"label": "Your Chart Says", "text": " ".join(overview_parts)})

        # 2. Key planet analysis
        planet_insights = []
        for pname in area["key_planets"]:
            p = next((p for p in planets if p["planet"] == pname), None)
            if not p:
                continue
            p_house = planet_house_map.get(pname)
            if not p_house:
                continue
            en_name = PLANET_NAMES.get(pname, pname)
            context = AREA_PLANET_CONTEXT.get(area["id"], {}).get(pname, "")
            p_reading = SIMPLE_PLANET_IN_HOUSE.get(pname, {}).get(p_house, "")
            retro_tag = " (Vakri/Retrograde)" if p.get("retrograde") else ""
            insight = f"**{pname} ({en_name}){retro_tag}** in House {p_house}. {context}."
            if p_reading:
                insight += f" {p_reading}"
            if p.get("retrograde"):
                from kundli.readings import RETROGRADE_EFFECTS
                retro_note = RETROGRADE_EFFECTS.get(pname, {}).get("simple", "")
                if retro_note:
                    insight += f" Being retrograde: {retro_note}"
            planet_insights.append(insight)

        if planet_insights:
            sections.append({"label": "Key Planets", "bullets": planet_insights[:3]})

        # 3. Current period influence
        if current_dasha:
            influences = []
            for hnum in area["houses"]:
                inf = DASHA_HOUSE_INFLUENCE.get(current_dasha, {}).get(hnum, "")
                if inf:
                    influences.append(inf)
            if influences:
                en_dasha = PLANET_NAMES.get(current_dasha, current_dasha)
                period_text = (
                    f"During your current **{current_dasha} ({en_dasha}) Mahadasha**, "
                    f"here's what to expect: {' '.join(influences[:2])}"
                )
                sections.append({"label": "Right Now", "text": period_text})

        # 4. Strengths & watch-outs
        strengths = []
        watchouts = []
        for hnum in area["houses"]:
            sign = houses[hnum - 1]["sign"]
            lord = SIGN_LORDS[sign]
            lord_house = planet_house_map.get(lord)
            occupants = _occupants(hnum)
            aspectors = get_aspecting_planets(planets, sign)

            if lord_house == hnum:
                strengths.append(f"The lord of House {hnum} is strong in its own house, naturally boosting this area.")
            if "Guru" in [o["planet"] for o in occupants]:
                strengths.append(f"Jupiter (Guru) blesses House {hnum} with wisdom and expansion.")
            if "Shukra" in [o["planet"] for o in occupants] and area["id"] in ("love", "wealth", "family"):
                strengths.append(f"Venus (Shukra) in House {hnum} brings comfort and harmony here.")
            if "Shani" in [o["planet"] for o in occupants] and area["id"] not in ("career",):
                watchouts.append(f"Saturn (Shani) in House {hnum} may bring delays or extra responsibilities.")
            if "Rahu" in [o["planet"] for o in occupants]:
                watchouts.append(f"Rahu in House {hnum} brings intensity and unconventional experiences.")
            if "Mangal" in aspectors and area["id"] in ("love", "family"):
                watchouts.append(f"Mars aspects House {hnum}, watch for occasional conflicts or impatience.")

        tips = []
        if strengths:
            tips.append("✅ " + " ".join(strengths[:2]))
        if watchouts:
            tips.append("⚠️ " + " ".join(watchouts[:2]))
        if tips:
            sections.append({"label": "Strengths & Watch-outs", "bullets": tips})

        results.append({
            "id": area["id"],
            "icon": area["icon"],
            "title": area["title"],
            "desc": area["desc"],
            "sections": sections,
        })

    return results
