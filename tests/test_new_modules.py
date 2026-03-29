"""Unit tests for new modules: doshas, shadbala, yogini dasha, ashtakavarga, insights, remedies, lifeareas."""
from datetime import datetime

from kundli.calc import (
    compute_planets, compute_houses, to_julian, build_planet_house_map,
    check_doshas, compute_shadbala, compute_yogini_dasha, SIGNS,
    compute_dasha, compute_antardasha,
)
from kundli.ashtakavarga import compute_ashtakavarga
from kundli.insights import generate_daily_insights
from kundli.remedies import DOSHA_REMEDIES, PLANET_REMEDIES
from kundli.lifeareas import generate_life_areas
from kundli.readings import build_house_readings
from kundli.names import PLANET_NAMES

# Reference data
BIRTH = datetime(1996, 9, 23, 22, 17)
JD = to_julian(BIRTH, 5.5)
PLANETS = compute_planets(JD)
HOUSES = compute_houses(JD, 30.734, 76.793)
PHM = build_planet_house_map(PLANETS, HOUSES)


class TestCheckDoshas:
    def test_returns_list(self):
        doshas = check_doshas(PLANETS, PHM)
        assert isinstance(doshas, list)
        assert len(doshas) >= 2  # Manglik + Kalsarpa at minimum

    def test_dosha_structure(self):
        for d in check_doshas(PLANETS, PHM):
            assert all(k in d for k in ["name", "present", "detail"])
            assert isinstance(d["present"], bool)
            assert len(d["detail"]) > 10

    def test_manglik_detection(self):
        doshas = check_doshas(PLANETS, PHM)
        manglik = next(d for d in doshas if d["name"] == "Manglik Dosha")
        # Mars in house 3 for reference chart = not Manglik
        assert manglik["present"] is False

    def test_manglik_positive(self):
        phm = {**PHM, "Mangal": 7}
        doshas = check_doshas(PLANETS, phm)
        manglik = next(d for d in doshas if d["name"] == "Manglik Dosha")
        assert manglik["present"] is True

    def test_sade_sati_with_saturn(self):
        moon_sign = next(p["sign"] for p in PLANETS if p["planet"] == "Chandra")
        # Saturn in same sign as Moon = peak Sade Sati
        doshas = check_doshas(PLANETS, PHM, moon_sign)
        sade_sati = next(d for d in doshas if d["name"] == "Sade Sati")
        assert sade_sati["present"] is True
        assert "Peak" in sade_sati["detail"]

    def test_sade_sati_absent(self):
        doshas = check_doshas(PLANETS, PHM, "Mesha")  # Far from Makara Moon
        sade_sati = next(d for d in doshas if d["name"] == "Sade Sati")
        assert sade_sati["present"] is False

    def test_no_sade_sati_without_saturn(self):
        doshas = check_doshas(PLANETS, PHM)  # No current_saturn_sign
        names = [d["name"] for d in doshas]
        assert "Sade Sati" not in names


class TestComputeShadbala:
    def test_returns_list(self):
        result = compute_shadbala(PLANETS, HOUSES, PHM)
        assert isinstance(result, list)

    def test_excludes_rahu_ketu(self):
        result = compute_shadbala(PLANETS, HOUSES, PHM)
        names = [r["planet"] for r in result]
        assert "Rahu" not in names
        assert "Ketu" not in names
        assert len(result) == 7

    def test_strength_range(self):
        for r in compute_shadbala(PLANETS, HOUSES, PHM):
            assert 0 <= r["strength"] <= 100
            assert r["label"] in ("Strong", "Moderate", "Weak")

    def test_sorted_descending(self):
        result = compute_shadbala(PLANETS, HOUSES, PHM)
        strengths = [r["strength"] for r in result]
        assert strengths == sorted(strengths, reverse=True)


class TestComputeYoginiDasha:
    def test_returns_list(self):
        result = compute_yogini_dasha(290.27, BIRTH)
        assert isinstance(result, list)
        assert len(result) >= 20

    def test_starts_at_birth(self):
        result = compute_yogini_dasha(290.27, BIRTH)
        assert result[0]["start"] == BIRTH

    def test_contiguous(self):
        result = compute_yogini_dasha(290.27, BIRTH)
        for i in range(len(result) - 1):
            gap = abs((result[i]["end"] - result[i + 1]["start"]).total_seconds())
            assert gap < 1

    def test_valid_yogini_names(self):
        from kundli.calc import YOGINI_NAMES
        result = compute_yogini_dasha(290.27, BIRTH)
        for d in result:
            assert d["lord"] in YOGINI_NAMES

    def test_cycle_repeats(self):
        result = compute_yogini_dasha(290.27, BIRTH)
        # After 8 full periods, the sequence should repeat
        lords = [d["lord"] for d in result]
        # First lord appears again later
        assert lords.count(lords[0]) >= 2


class TestAshtakavarga:
    def test_sav_sum_337(self):
        result = compute_ashtakavarga(PLANETS, HOUSES)
        assert sum(result["sav"]) == 337

    def test_sav_12_signs(self):
        result = compute_ashtakavarga(PLANETS, HOUSES)
        assert len(result["sav"]) == 12

    def test_bav_7_planets(self):
        result = compute_ashtakavarga(PLANETS, HOUSES)
        assert len(result["bav"]) == 7

    def test_bav_values_range(self):
        result = compute_ashtakavarga(PLANETS, HOUSES)
        for planet, points in result["bav"].items():
            assert len(points) == 12
            for p in points:
                assert 0 <= p <= 8

    def test_signs_list(self):
        result = compute_ashtakavarga(PLANETS, HOUSES)
        assert result["signs"] == SIGNS


class TestDailyInsights:
    def test_returns_list(self):
        transits = [{"planet": "Surya", "sign": "Mesha", "degree": 10.0, "house": 1}]
        result = generate_daily_insights(transits)
        assert isinstance(result, list)

    def test_insight_structure(self):
        transits = [{"planet": "Guru", "sign": "Mesha", "degree": 10.0, "house": 5}]
        result = generate_daily_insights(transits)
        assert len(result) == 1
        assert all(k in result[0] for k in ["planet", "house", "text"])

    def test_all_houses_covered(self):
        for h in range(1, 13):
            transits = [{"planet": "Surya", "sign": "Mesha", "degree": 10.0, "house": h}]
            result = generate_daily_insights(transits)
            assert len(result) == 1, f"No insight for Surya in house {h}"

    def test_unknown_planet_skipped(self):
        transits = [{"planet": "Rahu", "sign": "Mesha", "degree": 10.0, "house": 1}]
        result = generate_daily_insights(transits)
        assert len(result) == 0


class TestRemedies:
    def test_dosha_remedies_keys(self):
        assert "Manglik Dosha" in DOSHA_REMEDIES
        assert "Kalsarpa Dosha" in DOSHA_REMEDIES
        assert "Sade Sati" in DOSHA_REMEDIES

    def test_dosha_remedies_non_empty(self):
        for name, remedies in DOSHA_REMEDIES.items():
            assert len(remedies) >= 3, f"{name} has too few remedies"

    def test_planet_remedies_all_planets(self):
        expected = {"Surya", "Chandra", "Mangal", "Budh", "Guru", "Shukra", "Shani", "Rahu", "Ketu"}
        assert set(PLANET_REMEDIES.keys()) == expected

    def test_planet_remedy_structure(self):
        for planet, remedy in PLANET_REMEDIES.items():
            assert all(k in remedy for k in ["gemstone", "mantra", "day", "donation", "practice"]), f"{planet} missing keys"


class TestLifeAreas:
    def setup_method(self):
        moon = next(p for p in PLANETS if p["planet"] == "Chandra")
        dashas = compute_antardasha(compute_dasha(moon["longitude"], BIRTH))
        now = datetime(2026, 3, 26, 12, 0)
        readings, current_dasha = build_house_readings(PLANETS, HOUSES, dashas, now, PHM)
        self.life_areas = generate_life_areas(PLANETS, HOUSES, dashas, current_dasha, PHM)

    def test_returns_list(self):
        assert isinstance(self.life_areas, list)
        assert len(self.life_areas) >= 6

    def test_area_structure(self):
        for la in self.life_areas:
            assert "id" in la
            assert "title" in la
            assert "icon" in la
            assert "sections" in la
            assert len(la["sections"]) >= 1

    def test_has_career_and_love(self):
        ids = {la["id"] for la in self.life_areas}
        assert "career" in ids
        assert "love" in ids
