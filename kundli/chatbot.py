"""Rule-based chatbot for Kundli Q&A."""
import re
from datetime import datetime, timedelta, timezone

from kundli.readings import SIMPLE_DASHA_EFFECTS

# Topic keywords mapped to house numbers
TOPIC_HOUSES = {
    "career": [10], "job": [10], "work": [10, 6], "profession": [10], "promotion": [10],
    "interview": [10, 6], "hire": [10], "placement": [10], "transfer": [10],
    "business": [7, 10], "money": [2, 11], "wealth": [2, 11], "finance": [2, 11],
    "income": [11], "salary": [2, 11], "invest": [2, 8, 11], "lottery": [5, 8, 11],
    "stock": [2, 5, 11], "stocks": [2, 5, 11], "loan": [6, 8],
    "marriage": [7], "spouse": [7], "partner": [7], "relationship": [7], "love": [5, 7],
    "romance": [5], "dating": [5, 7], "crush": [5, 7], "propose": [5, 7],
    "like me": [5, 7], "likes me": [5, 7], "interested in me": [5, 7],
    "breakup": [7, 12], "divorce": [7, 12], "ex come": [7, 12], "ex back": [7, 12],
    "health": [1, 6], "illness": [6], "disease": [6], "body": [1],
    "surgery": [6, 8], "recover": [1, 6], "treatment": [6],
    "children": [5], "kids": [5], "pregnancy": [5], "baby": [5], "conceive": [5],
    "education": [4, 5, 9], "study": [4, 5], "exam": [5], "college": [9], "university": [9],
    "pass": [5], "result": [5], "upsc": [5, 10], "neet": [5, 10], "jee": [5, 10],
    "travel": [3, 9, 12], "abroad": [9, 12], "foreign": [9, 12], "immigration": [12],
    "visa": [9, 12], "settle abroad": [9, 12], "relocat": [4, 9, 12],
    "home": [4], "house": [4], "property": [4], "real estate": [4], "vehicle": [4], "car": [4],
    "mother": [4], "father": [9], "parents": [4, 9],
    "sibling": [3], "brother": [3], "sister": [3],
    "spiritual": [9, 12], "religion": [9], "meditation": [12], "moksha": [12],
    "luck": [9], "fortune": [9],
    "enemy": [6], "competition": [6], "legal": [6], "court": [6], "debt": [6],
    "dispute": [6, 7], "case": [6],
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
    (r"(when.*marr|marriage.*timing|marriage.*when|when.*get.*married|vivah.*kab|shadi.*kab)", "marriage_timing"),
    (r"(love.*marr|arranged.*marr|love.*arranged)", "love_arranged"),
    (r"(marriage.*delay|late.*marr|delay.*marr|why.*not.*married)", "marriage_delay"),
    (r"(foreign.*settl|settle.*abroad|foreign.*yoga|move.*abroad.*perman)", "foreign_settlement"),
    (r"(business.*job|job.*business|own.*business|service.*business|start.*business.*or)", "business_vs_job"),
    (r"(good|bad|lucky|unlucky)\s*(time|period|phase)", "timing"),
    (r"(should i|can i|will i|will my|will he|will she|will this|will the|is it good|do i|does)", "advice"),
    (r"(compatible|compatibility|match)", "compatibility"),
    (r"(strength|strong|positive|good thing)", "strengths"),
    (r"(weakness|weak|negative|challenge|difficult)", "challenges"),
    (r"(summary|overview|overall|tell me about my chart)", "summary"),
    (r"(manglik|mangal dosha)", "manglik"),
    (r"(who are you|what are you|what can you do|help|hi$|hello|hey)", "greeting"),
    (r"(thank|thanks|ok|okay|bye|goodbye)", "closing"),
    (r"(what is|explain|meaning of).*(house|planet|sign|rashi|nakshatra|dasha|lagna|ascendant|graha)", "explain"),
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
    q = " " + question.lower() + " "
    houses = set()
    matched_topics = []
    for keyword, house_nums in TOPIC_HOUSES.items():
        # Use word boundary check to avoid partial matches like "art" in "start"
        if re.search(r'(?<![a-z])' + re.escape(keyword) + r'(?![a-z])', q):
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

        # Current antardasha
        for ad in current.get("antardasha", []):
            if ad["start"] <= now <= ad["end"]:
                ad_en = planet_names.get(ad["lord"], ad["lord"])
                answer += f"**Current Antardasha:** {ad['lord']} ({ad_en}), {ad['start'].strftime('%d %b %Y')} to {ad['end'].strftime('%d %b %Y')}\n\n"
                for pr in ad.get("pratyantar", []):
                    if pr["start"] <= now <= pr["end"]:
                        pr_en = planet_names.get(pr["lord"], pr["lord"])
                        answer += f"**Current Pratyantar:** {pr['lord']} ({pr_en}), {pr['start'].strftime('%d %b %Y')} to {pr['end'].strftime('%d %b %Y')}\n\n"
                        break
                break

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


def _build_marriage_timing_answer(dashas, planets, houses, current_dasha, planet_names, tz_offset):
    """Analyze marriage timing from 7th house lord dasha and Venus/Jupiter periods."""
    from kundli.core import SIGN_LORDS_CALC
    now = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=tz_offset)

    seventh_sign = houses[6]["sign"]
    seventh_lord = SIGN_LORDS_CALC[seventh_sign]
    seventh_lord_en = planet_names.get(seventh_lord, seventh_lord)
    venus = next(p for p in planets if p["planet"] == "Shukra")

    answer = f"**Marriage Timing Analysis**\n\n"
    answer += f"Your 7th house (marriage) is in **{seventh_sign}**, ruled by **{seventh_lord} ({seventh_lord_en})**.\n\n"

    # Find dasha/antardasha periods of 7th lord, Venus, Jupiter
    marriage_planets = {seventh_lord, "Shukra", "Guru"}
    favorable = []
    for d in dashas:
        if d["lord"] in marriage_planets:
            label = f"{d['lord']} ({planet_names.get(d['lord'], d['lord'])}) Mahadasha"
            status = "current" if d["start"] <= now <= d["end"] else ("upcoming" if d["start"] > now else "past")
            favorable.append({"label": label, "start": d["start"], "end": d["end"], "status": status})
        for ad in d.get("antardasha", []):
            if ad["lord"] in marriage_planets and d["lord"] not in marriage_planets:
                label = f"{ad['lord']} ({planet_names.get(ad['lord'], ad['lord'])}) Antardasha in {d['lord']} MD"
                status = "current" if ad["start"] <= now <= ad["end"] else ("upcoming" if ad["start"] > now else "past")
                favorable.append({"label": label, "start": ad["start"], "end": ad["end"], "status": status})

    current_periods = [f for f in favorable if f["status"] == "current"]
    upcoming_periods = [f for f in favorable if f["status"] == "upcoming"]

    if current_periods:
        answer += "**Currently active favorable periods:**\n"
        for p in current_periods:
            answer += f"• {p['label']}: {p['start'].strftime('%b %Y')} to {p['end'].strftime('%b %Y')}\n"
        answer += "\n"

    if upcoming_periods:
        answer += "**Upcoming favorable windows:**\n"
        for p in upcoming_periods[:4]:
            answer += f"• {p['label']}: {p['start'].strftime('%b %Y')} to {p['end'].strftime('%b %Y')}\n"
        answer += "\n"

    answer += (f"Periods of **{seventh_lord}** (7th lord), **Shukra** (Venus, natural marriage significator), "
               f"and **Guru** (Jupiter, blessings) are traditionally considered favorable for marriage. "
               f"These are tendencies, not certainties. The actual timing also depends on transits and the partner's chart.")

    return answer


def _get_phm(planets, houses, planet_house_map=None):
    """Get or build planet_house_map."""
    if planet_house_map:
        return planet_house_map
    from kundli.planets import build_planet_house_map
    return build_planet_house_map(planets, houses)


def _build_love_arranged_answer(planets, houses, planet_names, planet_house_map=None):
    """Analyze love vs arranged marriage indicators."""
    from kundli.core import SIGN_LORDS_CALC, EXALTATION, OWN_SIGNS, _get
    phm = _get_phm(planets, houses, planet_house_map)
    venus = _get(planets, "Shukra")
    lord7 = SIGN_LORDS_CALC[houses[6]["sign"]]
    lord5 = SIGN_LORDS_CALC[houses[4]["sign"]]
    rahu_house = phm.get("Rahu")
    venus_strong = venus["sign"] in (EXALTATION.get("Shukra", ""), *OWN_SIGNS.get("Shukra", []))
    lord5_house = phm.get(lord5)
    lord7_house = phm.get(lord7)
    indicators = []
    if lord5_house == lord7_house:
        indicators.append("5th lord (romance) and 7th lord (marriage) are in the same house, suggesting love leading to marriage")
    if rahu_house == 7:
        indicators.append("Rahu in 7th house suggests an unconventional or cross-cultural partnership")
    if venus_strong:
        indicators.append(f"Venus is strong in {venus['sign']}, supporting romantic fulfillment")
    if phm.get("Shukra") in (5, 7):
        indicators.append(f"Venus in House {phm['Shukra']} strengthens romantic connections")
    answer = "**Love vs Arranged Marriage Indicators**\n\n"
    answer += f"7th house lord: **{lord7} ({planet_names.get(lord7, lord7)})** in House {lord7_house}\n"
    answer += f"5th house lord: **{lord5} ({planet_names.get(lord5, lord5)})** in House {lord5_house}\n\n"
    if indicators:
        answer += "Your chart suggests:\n" + "\n".join(f"- {i}" for i in indicators) + "\n\n"
    else:
        answer += "No strong indicators either way. Both paths are equally supported.\n\n"
    answer += "These are tendencies, not certainties. Personal choice always matters most."
    return answer


def _build_marriage_delay_answer(planets, houses, planet_names, planet_house_map=None):
    """Analyze factors that may delay marriage."""
    from kundli.core import SIGN_LORDS_CALC, _get
    from kundli.planets import get_aspecting_planets
    phm = _get_phm(planets, houses, planet_house_map)
    seventh_sign = houses[6]["sign"]
    lord7 = SIGN_LORDS_CALC[seventh_sign]
    lord7_house = phm.get(lord7)
    aspecting = get_aspecting_planets(planets, seventh_sign)
    factors = []
    if phm.get("Shani") == 7 or "Shani" in aspecting:
        factors.append("Saturn influences the 7th house, often indicating a mature, deliberate approach to marriage")
    if phm.get("Rahu") == 7 or "Rahu" in aspecting:
        factors.append("Rahu's influence on the 7th house suggests unconventional timing or partner selection")
    if phm.get("Ketu") == 7 or "Ketu" in aspecting:
        factors.append("Ketu in the 7th house indicates a spiritual or detached approach to partnerships")
    if lord7_house in (6, 8, 12):
        factors.append(f"7th lord {lord7} is in House {lord7_house} (a challenging house), which can delay but also deepen the eventual bond")
    sun = _get(planets, "Surya")
    venus = _get(planets, "Shukra")
    if abs(sun["longitude"] - venus["longitude"]) < 10:
        factors.append("Venus is close to the Sun (combust), which may temporarily dim relationship energy")
    answer = "**Marriage Timing Factors**\n\n"
    if factors:
        answer += "Your chart shows these influences:\n" + "\n".join(f"- {i}" for i in factors) + "\n\n"
        answer += "These placements often indicate a more thoughtful path to marriage, not denial of it. Late marriages are frequently the most stable."
    else:
        answer += "No major delay factors found. The 7th house and its lord are relatively unafflicted."
    return answer


def _build_foreign_settlement_answer(planets, houses, planet_names, planet_house_map=None):
    """Analyze foreign settlement yoga indicators."""
    from kundli.core import SIGN_LORDS_CALC
    phm = _get_phm(planets, houses, planet_house_map)
    lord12 = SIGN_LORDS_CALC[houses[11]["sign"]]
    lord4 = SIGN_LORDS_CALC[houses[3]["sign"]]
    lord9 = SIGN_LORDS_CALC[houses[8]["sign"]]
    indicators = []
    rahu_house = phm.get("Rahu")
    if rahu_house in (7, 9, 12):
        indicators.append(f"Rahu in House {rahu_house}, a classic indicator of foreign connections")
    if phm.get(lord12) in (1, 9):
        indicators.append(f"12th lord ({lord12}) in House {phm[lord12]}, linking foreign lands to self/fortune")
    if phm.get(lord4) == 12 or phm.get(lord12) == 4:
        indicators.append("Connection between 4th house (homeland) and 12th house (foreign lands)")
    if phm.get(lord9) in (3, 9, 12):
        indicators.append(f"9th lord ({lord9}) supports long-distance travel and foreign residence")
    answer = "**Foreign Settlement Yoga Analysis**\n\n"
    if indicators:
        answer += "Your chart shows these foreign settlement indicators:\n" + "\n".join(f"- {i}" for i in indicators) + "\n\n"
        answer += f"Strength: {len(indicators)} of 4 indicators present. " + ("Strong" if len(indicators) >= 3 else "Moderate" if len(indicators) >= 2 else "Mild") + " foreign settlement yoga."
    else:
        answer += "No strong foreign settlement indicators found. Your chart favors staying closer to your place of birth."
    return answer


def _build_business_vs_job_answer(planets, houses, planet_names, planet_house_map=None):
    """Compare business vs service indicators."""
    from kundli.core import SIGN_LORDS_CALC
    phm = _get_phm(planets, houses, planet_house_map)
    lord7 = SIGN_LORDS_CALC[houses[6]["sign"]]
    lord10 = SIGN_LORDS_CALC[houses[9]["sign"]]
    biz_score, job_score = 0, 0
    # 7th house strength (business)
    if phm.get(lord7) in (1, 4, 7, 10):
        biz_score += 2
    biz_planets = [p for p in planets if phm.get(p["planet"]) == 7 and p["planet"] not in ("Rahu", "Ketu")]
    biz_score += len(biz_planets)
    # 10th house strength (service)
    if phm.get(lord10) in (1, 4, 7, 10):
        job_score += 2
    job_planets = [p for p in planets if phm.get(p["planet"]) == 10 and p["planet"] not in ("Rahu", "Ketu")]
    job_score += len(job_planets)
    # Mercury/Jupiter boost for business
    if phm.get("Budh") in (7, 10, 11):
        biz_score += 1
    if phm.get("Guru") in (7, 9, 11):
        biz_score += 1
    answer = "**Business vs Job Analysis**\n\n"
    answer += f"7th house (business) lord: **{lord7}** in House {phm.get(lord7)} (score: {biz_score})\n"
    answer += f"10th house (career) lord: **{lord10}** in House {phm.get(lord10)} (score: {job_score})\n\n"
    if biz_score > job_score:
        answer += "Your chart shows stronger indicators for **independent business or partnerships**."
    elif job_score > biz_score:
        answer += "Your chart shows stronger indicators for **professional service or employment**."
    else:
        answer += "Both paths are equally supported. You could succeed in either."
    answer += "\n\nThis is a tendency, not a rule. Many successful entrepreneurs have strong 10th houses and vice versa."
    return answer


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

def _build_topic_timing(house_nums, topics, dashas, houses, planet_names, tz_offset):
    """Build dasha timing analysis for specific life topics."""
    from kundli.core import SIGN_LORDS_CALC
    now = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=tz_offset)

    # Find lords of relevant houses
    relevant_lords = set()
    house_lord_labels = []
    for h in house_nums:
        sign = houses[h - 1]["sign"]
        lord = SIGN_LORDS_CALC[sign]
        relevant_lords.add(lord)
        house_lord_labels.append(f"House {h} lord {lord} ({planet_names.get(lord, lord)})")

    answer = f"**Timing for {', '.join(topics)}:**\n\n"
    answer += "Relevant house lords: " + ", ".join(house_lord_labels) + "\n\n"

    # Find current and upcoming periods of relevant lords
    current = []
    upcoming = []
    for d in dashas:
        if d["lord"] in relevant_lords:
            if d["start"] <= now <= d["end"]:
                current.append(f"{d['lord']} ({planet_names.get(d['lord'], d['lord'])}) Mahadasha: {d['start'].strftime('%b %Y')} to {d['end'].strftime('%b %Y')}")
            elif d["start"] > now:
                upcoming.append(f"{d['lord']} ({planet_names.get(d['lord'], d['lord'])}) Mahadasha: {d['start'].strftime('%b %Y')} to {d['end'].strftime('%b %Y')}")
        for ad in d.get("antardasha", []):
            if ad["lord"] in relevant_lords and d["lord"] not in relevant_lords:
                if ad["start"] <= now <= ad["end"]:
                    current.append(f"{ad['lord']} ({planet_names.get(ad['lord'], ad['lord'])}) Antardasha: {ad['start'].strftime('%b %Y')} to {ad['end'].strftime('%b %Y')}")
                elif ad["start"] > now and len(upcoming) < 4:
                    upcoming.append(f"{ad['lord']} ({planet_names.get(ad['lord'], ad['lord'])}) Antardasha: {ad['start'].strftime('%b %Y')} to {ad['end'].strftime('%b %Y')}")

    if current:
        answer += "**Currently active favorable periods:**\n"
        for p in current:
            answer += f"• {p}\n"
        answer += "\nThe relevant house lord is active right now, which supports progress in this area.\n\n"
    else:
        answer += "The relevant house lords are not in their major or sub-period right now.\n\n"

    if upcoming:
        answer += "**Upcoming favorable windows:**\n"
        for p in upcoming[:3]:
            answer += f"• {p}\n"
        answer += "\n"

    answer += "These are periods when the planetary energy supports this area of life. Results also depend on effort, transits, and overall chart strength."
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
    if general == "marriage_timing":
        return _build_marriage_timing_answer(dashas, planets, houses, current_dasha, planet_names, chart_context.get("tz_offset", 5.5)), 0.9
    if general == "love_arranged":
        return _build_love_arranged_answer(planets, houses, planet_names, planet_house_map=chart_context.get("planet_house_map")), 0.9
    if general == "marriage_delay":
        return _build_marriage_delay_answer(planets, houses, planet_names, planet_house_map=chart_context.get("planet_house_map")), 0.9
    if general == "foreign_settlement":
        return _build_foreign_settlement_answer(planets, houses, planet_names, planet_house_map=chart_context.get("planet_house_map")), 0.9
    if general == "business_vs_job":
        return _build_business_vs_job_answer(planets, houses, planet_names, planet_house_map=chart_context.get("planet_house_map")), 0.9
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
        if general in ("advice", "timing") and topics:
            answer += "\n\n---\n\n"
            answer += _build_topic_timing(house_nums, topics, dashas, houses, planet_names, chart_context.get("tz_offset", 5.5))
        return answer, 0.85

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
            "Try rephrasing your question, pick one of these topics, or check the FAQ at /faq.")
