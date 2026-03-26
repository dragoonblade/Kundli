"""Tests for refactored modules — direct imports from core, planets, dasha, yogas, doshas, strength, varga."""
from datetime import datetime

from kundli.core import (
    PLANETS, SIGNS, NAKSHATRAS, NAKSHATRA_LORDS, ASPECTS,
    EXALTATION, OWN_SIGNS, SIGN_LORDS_CALC,
    get_sign, get_nakshatra, to_julian, _get, _sign_index,
)
from kundli.planets import (
    compute_planets, compute_houses, build_planet_house_map,
    compute_aspects, get_aspecting_planets,
)
from kundli.dasha import (
    DASHA_YEARS, DASHA_ORDER, DASHA_TOTAL_YEARS,
    YOGINI_NAMES, YOGINI_YEARS, YOGINI_TOTAL,
    compute_dasha, compute_antardasha, compute_pratyantar,
    compute_yogini_dasha,
)
from kundli.yogas import YOGAS, check_yogas
from kundli.doshas import check_doshas
from kundli.strength import compute_shadbala
from kundli.varga import DIVISIONAL_CHARTS, compute_divisional_chart

# Reference data
BIRTH = datetime(1996, 9, 23, 22, 17)
JD = to_julian(BIRTH, 5.5)
PLANET_LIST = compute_planets(JD)
HOUSE_LIST = compute_houses(JD, 30.734, 76.793)
PHM = build_planet_house_map(PLANET_LIST, HOUSE_LIST)


class TestCoreDirectImports:
    """Verify core.py exports work directly."""

    def test_constants_present(self):
        assert len(SIGNS) == 12
        assert len(NAKSHATRAS) == 27
        assert len(NAKSHATRA_LORDS) == 9
        assert len(PLANETS) == 8  # dict of swe IDs, excludes Ketu
        assert len(ASPECTS) == 9
        assert len(EXALTATION) == 7
        assert len(SIGN_LORDS_CALC) == 12

    def test_get_sign_direct(self):
        assert get_sign(0.0) == ("Mesha", 0.0)
        assert get_sign(45.0)[0] == "Vrishabha"

    def test_get_nakshatra_direct(self):
        nak, pada = get_nakshatra(0.0)
        assert nak == "Ashwini"
        assert pada == 1

    def test_to_julian_direct(self):
        jd = to_julian(BIRTH, 5.5)
        assert abs(jd - 2450350.1993) < 0.001

    def test_get_helper(self):
        moon = _get(PLANET_LIST, "Chandra")
        assert moon["planet"] == "Chandra"
        assert moon["sign"] == "Makara"

    def test_sign_index_helper(self):
        idx = _sign_index(PLANET_LIST, "Chandra")
        assert idx == SIGNS.index("Makara")


class TestPlanetsDirectImports:
    """Verify planets.py exports work directly."""

    def test_compute_planets(self):
        planets = compute_planets(JD)
        assert len(planets) == 9
        names = {p["planet"] for p in planets}
        assert "Ketu" in names

    def test_compute_houses(self):
        houses = compute_houses(JD, 30.734, 76.793)
        assert len(houses) == 12
        assert houses[0]["sign"] == "Vrishabha"

    def test_build_planet_house_map(self):
        phm = build_planet_house_map(PLANET_LIST, HOUSE_LIST)
        assert len(phm) == 9
        assert all(1 <= v <= 12 for v in phm.values())

    def test_compute_aspects(self):
        aspects = compute_aspects(PLANET_LIST)
        assert isinstance(aspects, list)
        for a in aspects:
            assert a["from"] not in a["to"]

    def test_get_aspecting_planets(self):
        result = get_aspecting_planets(PLANET_LIST, "Mesha")
        assert isinstance(result, list)


class TestDashaDirectImports:
    """Verify dasha.py exports work directly."""

    def test_dasha_constants(self):
        assert sum(DASHA_YEARS.values()) == DASHA_TOTAL_YEARS == 120
        assert len(DASHA_ORDER) == 9
        assert len(YOGINI_NAMES) == 8
        assert sum(YOGINI_YEARS) == YOGINI_TOTAL == 36

    def test_compute_dasha(self):
        dashas = compute_dasha(290.27, BIRTH)
        assert len(dashas) == 9
        assert dashas[0]["start"] == BIRTH

    def test_compute_antardasha(self):
        dashas = compute_antardasha(compute_dasha(290.27, BIRTH))
        for d in dashas:
            assert len(d["antardasha"]) == 9

    def test_compute_pratyantar(self):
        dashas = compute_pratyantar(compute_antardasha(compute_dasha(290.27, BIRTH)))
        count = sum(len(ad["pratyantar"]) for d in dashas for ad in d["antardasha"])
        assert count == 729

    def test_compute_yogini_dasha(self):
        result = compute_yogini_dasha(290.27, BIRTH)
        assert len(result) >= 20
        assert result[0]["start"] == BIRTH
        assert all(d["lord"] in YOGINI_NAMES for d in result)


class TestYogasDirectImports:
    """Verify yogas.py exports work directly."""

    def test_yogas_list(self):
        assert len(YOGAS) == 14
        for y in YOGAS:
            assert "name" in y and "desc" in y and "check" in y

    def test_check_yogas_basic(self):
        result = check_yogas(PLANET_LIST)
        assert isinstance(result, list)

    def test_check_yogas_with_houses(self):
        result = check_yogas(PLANET_LIST, HOUSE_LIST, PHM)
        assert len(result) >= len(check_yogas(PLANET_LIST))


class TestDoshasDirectImports:
    """Verify doshas.py exports work directly."""

    def test_check_doshas(self):
        doshas = check_doshas(PLANET_LIST, PHM)
        assert len(doshas) >= 2
        names = [d["name"] for d in doshas]
        assert "Manglik Dosha" in names
        assert "Kalsarpa Dosha" in names

    def test_sade_sati_direct(self):
        moon_sign = _get(PLANET_LIST, "Chandra")["sign"]
        doshas = check_doshas(PLANET_LIST, PHM, moon_sign)
        sade_sati = next(d for d in doshas if d["name"] == "Sade Sati")
        assert sade_sati["present"] is True


class TestStrengthDirectImports:
    """Verify strength.py exports work directly."""

    def test_compute_shadbala(self):
        result = compute_shadbala(PLANET_LIST, HOUSE_LIST, PHM)
        assert len(result) == 7
        assert all(r["planet"] not in ("Rahu", "Ketu") for r in result)
        assert all(0 <= r["strength"] <= 100 for r in result)


class TestVargaDirectImports:
    """Verify varga.py exports work directly."""

    def test_divisional_charts_constant(self):
        assert len(DIVISIONAL_CHARTS) == 17
        assert "D-9" in DIVISIONAL_CHARTS

    def test_compute_divisional_chart(self):
        d9 = compute_divisional_chart(PLANET_LIST, 9)
        assert len(d9) == 9
        for p in d9:
            assert p["sign"] in SIGNS


class TestFacadeStillWorks:
    """Verify calc.py facade re-exports everything."""

    def test_all_facade_imports(self):
        from kundli.calc import (
            PLANETS, SIGNS, NAKSHATRAS, NAKSHATRA_LORDS, ASPECTS,
            EXALTATION, OWN_SIGNS, SIGN_LORDS_CALC,
            get_sign, get_nakshatra, to_julian, _get, _sign_index,
            compute_planets, compute_houses, build_planet_house_map,
            compute_aspects, get_aspecting_planets,
            DASHA_YEARS, DASHA_ORDER, DASHA_TOTAL_YEARS,
            YOGINI_NAMES, YOGINI_YEARS, YOGINI_TOTAL,
            compute_dasha, compute_antardasha, compute_pratyantar,
            compute_yogini_dasha,
            YOGAS, check_yogas,
            check_doshas,
            compute_shadbala,
            DIVISIONAL_CHARTS, compute_divisional_chart,
        )
        # Just verify they're all importable and not None
        assert SIGNS is not None
        assert compute_planets is not None
        assert compute_dasha is not None
        assert check_yogas is not None
        assert check_doshas is not None
        assert compute_shadbala is not None
        assert compute_divisional_chart is not None
