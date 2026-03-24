"""Rule-based chatbot for Kundli Q&A."""
import re
from datetime import datetime, timedelta, timezone

from kundli.readings import SIMPLE_DASHA_EFFECTS

# Topic keywords mapped to house numbers
TOPIC_HOUSES = {
    "career": [10], "job": [10], "work": [10, 6], "profession": [10], "promotion": [10],
    "business": [7, 10], "money": [2, 11], "wealth": [2, 11], "finance": [2, 11],
    "income": [11], "salary": [2, 11],
    "marriage": [7], "spouse": [7], "partner": [7], "relationship": [7], "love": [5, 7],
    "romance": [5], "dating": [5, 7],
    "health": [1, 6], "illness": [6], "disease": [6], "body": [1],
    "children": [5], "kids": [5], "pregnancy": [5], "baby": [5],
    "education": [4, 5, 9], "study": [4, 5], "exam": [5], "college": [9], "university": [9],
    "travel": [3, 9, 12], "abroad": [9, 12], "foreign": [9, 12], "immigration": [12],
    "home": [4], "house": [4], "property": [4], "real estate": [4], "vehicle": [4], "car": [4],
    "mother": [4], "father": [9], "parents": [4, 9],
    "sibling": [3], "brother": [3], "sister": [3],
    "spiritual": [9, 12], "religion": [9], "meditation": [12], "moksha": [12],
    "luck": [9], "fortune": [9],
    "enemy": [6], "competition": [6], "legal": [6], "court": [6], "debt": [6],
    "personality": [1], "self": [1], "appearance": [1],
    "gain": [11], "friends": [11], "network": [11], "social": [11],
    "loss": [12], "expense": [12], "sleep": [12],
    "transformation": [8], "death": [8], "inheritance": [8], "occult": [8], "mystery": [8],
    "creativity": [5], "art": [5], "hobby": [3, 5],
}

# Dasha-related keywords
DASHA_KEYWORDS = ["dasha", "mahadasha", "period", "current period", "phase", "time", "now",
                   "this year", "right now", "currently", "present"]

# General question patterns
GENERAL_PATTERNS = [
    (r"(good|bad|lucky|unlucky)\s*(time|period|phase)", "timing"),
    (r"(should i|can i|will i|is it good)", "advice"),
    (r"(compatible|compatibility|match)", "compatibility"),
    (r"(strength|strong|positive|good thing)", "strengths"),
    (r"(weakness|weak|negative|challenge|difficult)", "challenges"),
    (r"(summary|overview|overall|tell me about my chart)", "summary"),
    (r"(manglik|mangal dosha)", "manglik"),
    (r"(who are you|what are you|what can you do|help|hi$|hello|hey)", "greeting"),
    (r"(thank|thanks|ok|okay|bye|goodbye)", "closing"),
    (r"(what is|explain|meaning of).*(house|planet|sign|nakshatra|dasha|lagna|ascendant)", "explain"),
    (r"(future|prediction|predict|next year|coming year|2026|2027)", "future"),
    (r"(remedy|remedies|solution|fix|improve|upay)", "remedies"),
    (r"(retrograde|vakri)", "retrograde"),
]

# Meta answers that don't need chart context
META_ANSWERS = {
    "greeting": (
        "I am your Kundli assistant. I can help you understand your Vedic birth chart "
        "and answer questions about different areas of your life based on your planetary positions.\n\n"
        "Here are some things you can ask me:\n\n"
        "- Tell me about my career\n"
        "- What does my chart say about marriage?\n"
        "- What is my current dasha period?\n"
        "- Give me a chart summary\n"
        "- Am I Manglik?\n"
        "- What are my strengths and challenges?\n"
        "- Tell me about my health, finances, education, or travel"
    ),
    "closing": "You're welcome! Feel free to come back anytime you have questions about your chart. 🙏",
    "remedies": (
        "Remedies are a traditional part of Vedic astrology, but they vary greatly depending on the "
        "specific planetary positions and the astrologer's school of thought. Common general practices include "
        "meditation, mantra chanting, gemstone recommendations, and charitable acts. For personalized remedies, "
        "it is best to consult a qualified Vedic astrologer who can study your chart in detail."
    ),
}


def _find_topics(question):
    """Find which houses are relevant to the question."""
    q = question.lower()
    houses = set()
    matched_topics = []
    for keyword, house_nums in TOPIC_HOUSES.items():
        if keyword in q:
            houses.update(house_nums)
            matched_topics.append(keyword)
    return sorted(houses), matched_topics


def _is_dasha_question(question):
    q = question.lower()
    return any(k in q for k in DASHA_KEYWORDS)


def _match_general(question):
    q = question.lower()
    for pattern, category in GENERAL_PATTERNS:
        if re.search(pattern, q):
            return category
    return None


def _build_house_answer(readings, house_nums, current_dasha):
    """Build answer from relevant house readings."""
    parts = []
    for r in readings:
        if r["num"] in house_nums:
            section = f"**House {r['num']}. {r['theme']}**\n"
            section += r["simple_summary"]
            if r["current_influence"]:
                section += f"\n\n🔮 *Current influence:* {r['current_influence']}"
            if r["simple_dasha_note"]:
                section += f"\n\n★ {r['simple_dasha_note']}"
            parts.append(section)
    return "\n\n---\n\n".join(parts)


def _build_dasha_answer(dashas, current_dasha, readings, planet_names, tz_offset=5.5):
    """Build answer about current dasha period."""
    effect = SIMPLE_DASHA_EFFECTS.get(current_dasha, "")
    en_name = planet_names.get(current_dasha, current_dasha)
    now = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=tz_offset)

    current = None
    for d in dashas:
        if d["lord"] == current_dasha and d.get("years"):
            if d["start"] <= now <= d["end"]:
                current = d
                break

    answer = f"You're currently in **{current_dasha} ({en_name}) Mahadasha**. {effect}.\n\n"
    if current:
        elapsed = (now - current["start"]).days / 365.25
        remaining = (current["end"] - now).days / 365.25
        answer += f"This period started on {current['start'].strftime('%d %b %Y')} and runs until {current['end'].strftime('%d %b %Y')} ({current['years']} years total). You're about {elapsed:.1f} years in, with ~{remaining:.1f} years remaining.\n\n"

    # Add key influences
    active_houses = [r for r in readings if r["current_influence"]]
    if active_houses:
        answer += "**Key areas affected right now:**\n\n"
        for r in active_houses[:4]:
            answer += f"• **{r['theme']}:** {r['current_influence']}\n\n"

    return answer


def _build_summary(readings, planets, houses, current_dasha, planet_names):
    """Build overall chart summary."""
    lagna = houses[0]
    en_lagna = planet_names.get(lagna["sign"], lagna["sign"]) if lagna["sign"] in planet_names else lagna["sign"]

    answer = f"**Your Chart at a Glance:**\n\n"
    answer += f"• **Ascendant (Lagna):** {lagna['sign']} ({en_lagna}), this shapes your personality and how the world sees you.\n"

    moon = next((p for p in planets if p["planet"] == "Chandra"), None)
    if moon:
        en_moon_sign = planet_names.get(moon["sign"], moon["sign"]) if moon["sign"] in planet_names else moon["sign"]
        answer += f"• **Moon Sign:** {moon['sign']} ({en_moon_sign}) in {moon['nakshatra']}, this is your emotional nature.\n"

    sun = next((p for p in planets if p["planet"] == "Surya"), None)
    if sun:
        en_sun_sign = planet_names.get(sun["sign"], sun["sign"]) if sun["sign"] in planet_names else sun["sign"]
        answer += f"• **Sun Sign:** {sun['sign']} ({en_sun_sign}), this is your core identity.\n"

    if current_dasha:
        effect = SIMPLE_DASHA_EFFECTS.get(current_dasha, "")
        answer += f"• **Current Period:** {current_dasha} ({planet_names.get(current_dasha, current_dasha)}) Mahadasha. {effect}.\n"

    # Highlight strongest houses (ones with planets)
    occupied = [r for r in readings if r["occupants"]]
    if occupied:
        answer += f"\n**Most active areas in your chart:**\n\n"
        for r in occupied[:5]:
            occ = ", ".join(r["occupants"])
            answer += f"• **{r['theme']}** (House {r['num']}): {occ} here. {r['simple_summary'][:120]}..\n"

    return answer


def _build_manglik_answer(planets, readings):
    """Check basic Manglik condition."""
    mars_house = None
    for r in readings:
        if "Mangal" in r["occupants"]:
            mars_house = r["num"]
            break
    if mars_house in [1, 2, 4, 7, 8, 12]:
        return (f"Based on your chart, **Mangal (Mars) is in House {mars_house}**, which is one of the "
                f"positions that indicates Manglik Dosha. This is traditionally considered important for "
                f"marriage compatibility. However, many astrologers believe the effects reduce after age 28, "
                f"and certain planetary combinations can cancel or reduce the dosha. "
                f"For a detailed analysis, consult a professional astrologer.")
    else:
        house_str = f"House {mars_house}" if mars_house else "a neutral position"
        return (f"Based on your chart, Mangal (Mars) is in {house_str}, which does **not** indicate "
                f"Manglik Dosha. Mars needs to be in houses 1, 2, 4, 7, 8, or 12 for Manglik consideration.")


def _build_strengths(readings):
    parts = ["**Your chart's strengths:**\n"]
    for r in readings:
        if r["lord_note"] and "own house" in r["lord_note"]:
            parts.append(f"• **{r['theme']}**, the lord is strong in its own house, boosting this area naturally.")
        if len(r["occupants"]) >= 2:
            parts.append(f"• **{r['theme']}**, multiple planets here ({', '.join(r['occupants'])}) make this a very active area.")
    if len(parts) == 1:
        parts.append("• Your chart has a balanced distribution, no single area is overwhelmingly dominant, which gives you flexibility in life.")
    return "\n".join(parts)


def _build_challenges(readings):
    parts = ["**Areas that may need attention:**\n"]
    for r in readings:
        if not r["occupants"] and r["lord_house"] and r["lord_house"] in [6, 8, 12]:
            parts.append(f"• **{r['theme']}**, the lord is placed in a challenging house, which may bring some obstacles here.")
    if len(parts) == 1:
        parts.append("• No major challenging placements detected. Focus on the houses where your current dasha is active for the best results.")
    return "\n".join(parts)



def _build_retrograde_answer(planets, planet_names):
    """List retrograde planets and their effects."""
    from kundli.readings import RETROGRADE_EFFECTS
    retro_planets = [p for p in planets if p.get("retrograde")]
    if not retro_planets:
        return "No planets are retrograde in your birth chart. All planets were moving in direct motion at the time of your birth."

    answer = f"**Retrograde (Vakri) planets in your chart: {len(retro_planets)}**\n\n"
    for p in retro_planets:
        en = planet_names.get(p["planet"], p["planet"])
        effect = RETROGRADE_EFFECTS.get(p["planet"], {}).get("simple", "")
        answer += f"**{p['planet']} ({en})** in {p['sign']} is retrograde."
        if effect:
            answer += f" {effect}"
        answer += "\n\n"
    answer += ("Retrograde planets are not negative. They indicate areas where energy is directed inward "
               "rather than outward, often giving deeper insight and unconventional strengths.")
    return answer

def rule_based_answer(question, chart_context):
    """Try to answer using rules. Returns (answer, confidence)."""
    readings = chart_context["house_readings"]
    current_dasha = chart_context["current_dasha"]
    planet_names = chart_context["planet_names"]
    planets = chart_context["planets"]
    houses = chart_context["houses"]
    dashas = chart_context["dashas"]

    # Check general patterns first
    general = _match_general(question)

    # Meta answers (don't need chart data)
    if general in META_ANSWERS:
        return META_ANSWERS[general], 1.0

    if general == "summary":
        return _build_summary(readings, planets, houses, current_dasha, planet_names), 0.9
    if general == "manglik":
        return _build_manglik_answer(planets, readings), 0.9
    if general == "strengths":
        return _build_strengths(readings), 0.8
    if general == "challenges":
        return _build_challenges(readings), 0.8
    if general == "future":
        return _build_dasha_answer(dashas, current_dasha, readings, planet_names, tz_offset=chart_context.get("tz_offset", 5.5)), 0.85
    if general == "explain":
        return _build_explain_answer(question, planets, houses, current_dasha, planet_names), 0.8
    if general == "retrograde":
        return _build_retrograde_answer(planets, planet_names), 0.9

    # Dasha questions
    if _is_dasha_question(question):
        return _build_dasha_answer(dashas, current_dasha, readings, planet_names, tz_offset=chart_context.get("tz_offset", 5.5)), 0.9

    # Topic-based house lookup
    house_nums, topics = _find_topics(question)
    if house_nums:
        answer = _build_house_answer(readings, house_nums, current_dasha)
        if general == "advice" and topics:
            answer += f"\n\n💡 Based on your chart, this is {'a favorable' if current_dasha else 'an active'} period for matters related to {', '.join(topics)}."
        return answer, 0.8

    # Timing/advice without specific topic
    if general in ("timing", "advice"):
        effect = SIMPLE_DASHA_EFFECTS.get(current_dasha, "")
        return (f"You're in **{current_dasha} Mahadasha**. {effect}. "
                f"Could you be more specific about what area you're asking about? "
                f"For example: career, marriage, health, finances, education, travel, etc."), 0.6

    return None, 0.0


def _build_explain_answer(question, planets, houses, current_dasha, planet_names):
    """Explain astrological concepts in context of the chart."""
    q = question.lower()
    if "lagna" in q or "ascendant" in q:
        sign = houses[0]["sign"]
        en = planet_names.get(sign, sign) if sign in planet_names else sign
        return (f"Your Lagna (Ascendant) is **{sign}** ({en}). "
                f"The Lagna is the zodiac sign that was rising on the eastern horizon at the exact moment of your birth. "
                f"It is considered the most important point in your chart because it determines the layout of all 12 houses "
                f"and strongly influences your personality, physical appearance, and overall life path.")
    if "dasha" in q:
        effect = SIMPLE_DASHA_EFFECTS.get(current_dasha, "")
        return (f"Dasha is the planetary period system used in Vedic astrology. The most common system is "
                f"Vimshottari Dasha, which divides your life into periods ruled by different planets, "
                f"each lasting a specific number of years.\n\n"
                f"Your current Mahadasha (major period) is ruled by **{current_dasha}** "
                f"({planet_names.get(current_dasha, current_dasha)}). {effect}.")
    if "nakshatra" in q:
        moon = next((p for p in planets if p["planet"] == "Chandra"), None)
        if moon:
            return (f"Nakshatras are the 27 lunar mansions in Vedic astrology. Each spans 13 degrees 20 minutes of the zodiac. "
                    f"Your Moon is in **{moon['nakshatra']}** (Pada {moon['pada']}). "
                    f"The Moon's nakshatra is especially important because it determines your Vimshottari Dasha sequence "
                    f"and reveals deeper aspects of your emotional nature and life patterns.")
    if "house" in q:
        return ("In Vedic astrology, your birth chart is divided into 12 houses, each governing a different area of life. "
                "House 1 is your self and personality, House 7 is marriage, House 10 is career, and so on. "
                "The sign on each house cusp and any planets placed there shape how that area of life unfolds for you. "
                "Try asking about a specific area like career, marriage, or health to see what your houses reveal.")
    if "planet" in q or "graha" in q:
        return ("Vedic astrology uses 9 celestial bodies called Navagraha: "
                "Surya (Sun), Chandra (Moon), Mangal (Mars), Budh (Mercury), Guru (Jupiter), "
                "Shukra (Venus), Shani (Saturn), Rahu (North Node), and Ketu (South Node). "
                "Each planet governs specific aspects of life and its placement in your chart "
                "determines how those energies manifest for you.")
    if "sign" in q or "rashi" in q:
        return ("There are 12 zodiac signs (Rashis) in Vedic astrology: "
                "Mesha (Aries), Vrishabha (Taurus), Mithuna (Gemini), Karka (Cancer), "
                "Simha (Leo), Kanya (Virgo), Tula (Libra), Vrishchika (Scorpio), "
                "Dhanu (Sagittarius), Makara (Capricorn), Kumbha (Aquarius), and Meena (Pisces). "
                "Each sign has unique qualities and is ruled by a specific planet.")
    return ("Vedic astrology (Jyotish) is an ancient Indian system that uses the positions of planets "
            "at the time of your birth to understand your life patterns. Try asking me to explain "
            "a specific concept like Lagna, Dasha, Nakshatra, houses, planets, or signs.")


def chat(question, chart_context):
    """Main chat entry point."""
    general = _match_general(question)
    if general in META_ANSWERS:
        return META_ANSWERS[general]

    if not chart_context:
        return "Please generate a birth chart first, then I can answer questions about it."

    answer, confidence = rule_based_answer(question, chart_context)

    if answer and confidence >= 0.5:
        return answer

    return ("I wasn't able to find a specific answer for that in your chart. "
            "Here are some topics I can help with:\n\n"
            "**Life areas:** career, marriage, health, finances, education, travel, family, spirituality\n\n"
            "**Chart analysis:** overall summary, strengths, challenges, Manglik dosha\n\n"
            "**Current period:** dasha details, predictions, timing\n\n"
            "**Learn:** explain lagna, dasha, nakshatra, houses, planets, signs\n\n"
            "**Remedies:** general guidance on astrological remedies\n\n"
            "Try rephrasing your question or pick one of these topics.")
