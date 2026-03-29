"""Rule-based chatbot for Kundli Q&A."""
import re

from kundli.readings import SIMPLE_DASHA_EFFECTS
from kundli.chatbot_builders import (
    _build_house_answer, _build_dasha_answer, _build_summary,
    _build_manglik_answer, _build_marriage_timing_answer,
    _build_love_arranged_answer, _build_marriage_delay_answer,
    _build_foreign_settlement_answer, _build_business_vs_job_answer,
    _build_strengths, _build_challenges, _build_retrograde_answer,
    _build_topic_timing, _build_explain_answer, _get_phm,
)

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

DASHA_KEYWORDS = ["dasha", "mahadasha", "period", "current period", "phase", "time", "now",
                   "this year", "right now", "currently", "present"]

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
        if re.search(r'(?<![a-z])' + re.escape(keyword) + r'(?![a-z])', q):
            houses.update(house_nums)
            matched_topics.append(keyword)
    return sorted(houses), matched_topics


def _is_dasha_question(question):
    """Check if the question is about dasha periods."""
    q = question.lower()
    return any(k in q for k in DASHA_KEYWORDS)


def _match_general(question):
    """Match question against general patterns."""
    q = question.lower()
    for pattern, category in GENERAL_PATTERNS:
        if re.search(pattern, q):
            return category
    return None


def rule_based_answer(question, chart_context):
    """Try to answer using rules. Returns (answer, confidence)."""
    readings = chart_context["house_readings"]
    current_dasha = chart_context["current_dasha"]
    planet_names = chart_context["planet_names"]
    planets = chart_context["planets"]
    houses = chart_context["houses"]
    dashas = chart_context["dashas"]

    general = _match_general(question)

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

    if _is_dasha_question(question):
        return _build_dasha_answer(dashas, current_dasha, readings, planet_names, tz_offset=chart_context.get("tz_offset", 5.5)), 0.9

    house_nums, topics = _find_topics(question)
    if house_nums:
        answer = _build_house_answer(readings, house_nums, current_dasha)
        if general in ("advice", "timing") and topics:
            answer += "\n\n---\n\n"
            answer += _build_topic_timing(house_nums, topics, dashas, houses, planet_names, chart_context.get("tz_offset", 5.5))
        return answer, 0.85

    if general in ("timing", "advice"):
        effect = SIMPLE_DASHA_EFFECTS.get(current_dasha, "")
        return (f"You're in **{current_dasha} Mahadasha**. {effect}. "
                f"Could you be more specific about what area you're asking about? "
                f"For example: career, marriage, health, finances, education, travel, etc."), 0.6

    return None, 0.0


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
