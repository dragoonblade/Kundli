"""Daily transit insights based on current sky positions vs birth chart."""

TRANSIT_INSIGHTS = {
    "Surya": {
        1: "Focus on self-expression and personal goals today",
        2: "Financial matters and family communication highlighted",
        3: "Good day for short trips, writing, and connecting with siblings",
        4: "Domestic matters and emotional well-being in focus",
        5: "Creative energy is high. Romance and children are favored",
        6: "Health awareness day. Tackle pending tasks and routines",
        7: "Partnerships and relationships take center stage",
        8: "Deep introspection. Research and transformation are favored",
        9: "Learning, travel, and spiritual pursuits energized",
        10: "Career visibility peaks. Authority figures notice you",
        11: "Social connections and income opportunities expand",
        12: "Rest and spiritual reflection needed. Avoid overcommitting",
    },
    "Chandra": {
        1: "Emotions run high. Trust your instincts today",
        2: "Comfort food and family bonding bring peace",
        3: "Mental agility peaks. Communicate your feelings",
        4: "Strong pull toward home and mother figures",
        5: "Romantic and creative mood. Enjoy artistic pursuits",
        6: "Emotional sensitivity to health. Nurture yourself",
        7: "Seek emotional connection with partner or close allies",
        8: "Intense feelings surface. Good for emotional healing",
        9: "Philosophical mood. Seek wisdom and meaning",
        10: "Public image tied to emotional expression today",
        11: "Friends and community bring emotional fulfillment",
        12: "Need for solitude and spiritual recharge",
    },
    "Mangal": {
        1: "High energy and drive. Take initiative on personal projects",
        2: "Assertive about finances. Avoid impulsive spending",
        3: "Courage in communication. Speak up boldly",
        4: "Channel energy into home improvements or property matters",
        5: "Competitive spirit in sports, games, and creative ventures",
        6: "Strong ability to overcome obstacles and rivals",
        7: "Passion in relationships. Watch for arguments",
        8: "Intense drive for transformation. Research favored",
        9: "Adventurous energy. Travel and bold learning",
        10: "Ambitious push in career. Leadership opportunities",
        11: "Drive to achieve goals through networking",
        12: "Hidden energy. Work behind the scenes",
    },
    "Guru": {
        1: "Optimism and growth in personal matters. Expand your horizons",
        2: "Financial growth and generous speech attract abundance",
        3: "Wisdom in communication. Teaching and mentoring favored",
        4: "Blessings for home, property, and educational pursuits",
        5: "Children, creativity, and romance blessed by Jupiter's grace",
        6: "Ability to overcome challenges with wisdom and faith",
        7: "Beneficial partnerships and harmonious relationships",
        8: "Spiritual transformation and unexpected gains possible",
        9: "Peak period for higher learning, travel, and dharma",
        10: "Career expansion and recognition from authority figures",
        11: "Gains through social connections and elder guidance",
        12: "Spiritual growth and charitable inclinations strengthened",
    },
    "Shani": {
        1: "Discipline and patience in personal matters. Slow but steady progress",
        2: "Conservative approach to finances serves you well",
        3: "Structured communication. Patience with siblings needed",
        4: "Responsibilities at home. Property matters need attention",
        5: "Serious approach to creativity. Delayed but lasting results",
        6: "Strong work ethic overcomes health and work challenges",
        7: "Commitment and responsibility in partnerships tested",
        8: "Deep karmic lessons. Patience through transformation",
        9: "Structured learning and disciplined spiritual practice",
        10: "Hard work in career pays off. Authority through effort",
        11: "Long-term goals and steady networking bring results",
        12: "Solitude and spiritual discipline bring inner peace",
    },
}


def generate_daily_insights(transits: list) -> list:
    """Generate personalized daily insights from transit positions."""
    insights = []
    for t in transits:
        planet = t["planet"]
        house = t["house"]
        text = TRANSIT_INSIGHTS.get(planet, {}).get(house)
        if text:
            insights.append({"planet": planet, "house": house, "text": text})
    return insights
