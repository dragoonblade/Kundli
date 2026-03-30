"""Tests for chatbot coverage — answer builders and routing."""
from datetime import datetime, timedelta, timezone

from kundli.calc import (
    compute_planets, compute_houses, compute_dasha, compute_antardasha,
    compute_pratyantar, to_julian, build_planet_house_map, check_yogas,
)
from kundli.readings import build_house_readings
from kundli.names import PLANET_NAMES
from kundli.chatbot import chat


# Build a full chart context once
BIRTH = datetime(1996, 9, 23, 22, 17)
JD = to_julian(BIRTH, 5.5)
PLANETS = compute_planets(JD)
HOUSES = compute_houses(JD, 30.734, 76.793)
PHM = build_planet_house_map(PLANETS, HOUSES)
DASHAS = compute_pratyantar(compute_antardasha(compute_dasha(
    next(p for p in PLANETS if p["planet"] == "Chandra")["longitude"], BIRTH
)))
NOW = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=5.5)
READINGS, CURRENT_DASHA = build_house_readings(PLANETS, HOUSES, DASHAS, NOW, PHM)

CTX = {
    "house_readings": READINGS,
    "current_dasha": CURRENT_DASHA,
    "planet_names": PLANET_NAMES,
    "planets": PLANETS,
    "houses": HOUSES,
    "dashas": DASHAS,
    "tz_offset": 5.5,
}


class TestChatRouting:
    def test_greeting(self):
        assert "Drishti assistant" in chat("hello", None)

    def test_no_context(self):
        assert "generate a birth chart" in chat("tell me about career", None)

    def test_summary(self):
        answer = chat("give me a summary of my chart", CTX)
        assert "Lagna" in answer or "Ascendant" in answer

    def test_manglik(self):
        answer = chat("am I manglik?", CTX)
        assert "Mangal" in answer or "Mars" in answer

    def test_strengths(self):
        answer = chat("what are my strengths?", CTX)
        assert "strength" in answer.lower()

    def test_challenges(self):
        answer = chat("what challenges does my chart show?", CTX)
        assert len(answer) > 30

    def test_career(self):
        answer = chat("tell me about my career", CTX)
        assert len(answer) > 50

    def test_marriage(self):
        answer = chat("what about marriage?", CTX)
        assert len(answer) > 50

    def test_marriage_timing(self):
        answer = chat("when will I get married?", CTX)
        assert "7th house" in answer.lower() or "marriage" in answer.lower()
        assert "Shukra" in answer or "Venus" in answer

    def test_marriage_timing_hindi(self):
        answer = chat("shadi kab hogi?", CTX)
        assert "marriage" in answer.lower() or "7th" in answer.lower()

    def test_health(self):
        answer = chat("tell me about health", CTX)
        assert len(answer) > 30

    def test_dasha(self):
        answer = chat("tell me about my future predictions", CTX)
        assert "Mahadasha" in answer

    def test_retrograde(self):
        answer = chat("tell me about retrograde planets", CTX)
        assert "retrograde" in answer.lower() or "Vakri" in answer

    def test_explain_house(self):
        answer = chat("what is a house in astrology?", CTX)
        assert len(answer) > 30

    def test_explain_dasha(self):
        answer = chat("explain what dasha means", CTX)
        assert len(answer) > 30

    def test_remedies(self):
        answer = chat("what remedies should I follow?", CTX)
        assert len(answer) > 30

    def test_unknown_question(self):
        answer = chat("xyzzy foobar nonsense", CTX)
        assert "topics I can help with" in answer or len(answer) > 20

    def test_exam_timing(self):
        answer = chat("will I pass my exam?", CTX)
        assert "House" in answer
        assert "Timing" in answer or "Mahadasha" in answer or "Antardasha" in answer

    def test_job_interview(self):
        answer = chat("will I get the job interview?", CTX)
        assert "House" in answer
        assert len(answer) > 100

    def test_crush_question(self):
        answer = chat("does she like me?", CTX)
        assert len(answer) > 50

    def test_lottery_question(self):
        answer = chat("will I win the lottery?", CTX)
        assert "House" in answer

    def test_visa_question(self):
        answer = chat("will my visa get approved?", CTX)
        assert len(answer) > 50

    def test_ex_come_back(self):
        answer = chat("will my ex come back?", CTX)
        assert len(answer) > 50

    def test_conceive_question(self):
        answer = chat("will I conceive?", CTX)
        assert "House" in answer

    def test_explain_nakshatra(self):
        answer = chat("explain what nakshatra means", CTX)
        assert "Shravana" in answer or "nakshatra" in answer.lower()

    def test_explain_planet(self):
        answer = chat("what is a planet in astrology?", CTX)
        assert "Navagraha" in answer

    def test_explain_sign(self):
        answer = chat("explain what rashi means", CTX)
        assert "Mesha" in answer

    def test_explain_lagna(self):
        answer = chat("explain lagna", CTX)
        assert "Ascendant" in answer or "Lagna" in answer

    def test_compatibility_question(self):
        answer = chat("are we compatible?", CTX)
        assert len(answer) > 20

    def test_manglik_positive(self):
        """Test Manglik detection when Mars IS in a Manglik house."""
        # Override readings so Mars appears in house 7
        modified_readings = []
        for r in READINGS:
            if r["num"] == 7:
                modified_readings.append({**r, "occupants": ["Mangal"]})
            else:
                modified_readings.append({**r, "occupants": [o for o in r["occupants"] if o != "Mangal"]})
        ctx = {**CTX, "house_readings": modified_readings}
        answer = chat("am I manglik?", ctx)
        assert "Manglik Dosha" in answer or "House 7" in answer

    def test_closing(self):
        answer = chat("thanks bye", None)
        assert len(answer) > 10

    def test_love_arranged(self):
        answer = chat("will I have love marriage or arranged?", CTX)
        assert "7th house" in answer.lower() or "love" in answer.lower()

    def test_marriage_delay(self):
        answer = chat("why is my marriage delayed?", CTX)
        assert "marriage" in answer.lower() or "7th" in answer.lower()

    def test_foreign_settlement(self):
        answer = chat("will I settle abroad?", CTX)
        assert "foreign" in answer.lower() or "settlement" in answer.lower()

    def test_business_vs_job(self):
        answer = chat("should I do business or job?", CTX)
        assert "business" in answer.lower() or "7th house" in answer.lower()
