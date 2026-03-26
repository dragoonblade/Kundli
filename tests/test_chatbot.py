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
        assert "Kundli assistant" in chat("hello", None)

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

    def test_closing(self):
        answer = chat("thanks bye", None)
        assert len(answer) > 10
