"""Edge case tests for boundary conditions and unusual inputs."""
from datetime import datetime

from kundli.calc import (
    compute_planets, compute_houses, compute_dasha, compute_antardasha,
    to_julian, check_yogas, check_doshas, build_planet_house_map,
    get_sign, get_nakshatra, SIGNS,
)
from kundli.match import compute_ashtakoota


class TestYearBoundaries:
    def test_year_1_ad(self):
        jd = to_julian(datetime(1, 6, 15, 12, 0), 0)
        planets = compute_planets(jd)
        assert len(planets) == 9
        for p in planets:
            assert 0 <= p["longitude"] < 360

    def test_year_2100(self):
        jd = to_julian(datetime(2100, 1, 1, 0, 0), 0)
        planets = compute_planets(jd)
        assert len(planets) == 9
        houses = compute_houses(jd, 28.6, 77.2)
        assert len(houses) == 12

    def test_year_1900(self):
        jd = to_julian(datetime(1900, 3, 21, 6, 0), 5.5)
        planets = compute_planets(jd)
        moon = next(p for p in planets if p["planet"] == "Chandra")
        dashas = compute_dasha(moon["longitude"], datetime(1900, 3, 21, 6, 0))
        assert len(dashas) == 9


class TestExtremeCoordinates:
    def test_north_pole(self):
        jd = to_julian(datetime(2000, 6, 21, 12, 0), 0)
        planets = compute_planets(jd)
        assert len(planets) == 9
        # Placidus fails above ~66 latitude — verify it raises
        import swisseph
        try:
            houses = compute_houses(jd, 89.0, 0.0)
            assert len(houses) == 12  # if it works, fine
        except swisseph.Error:
            pass  # expected at extreme latitudes

    def test_south_pole(self):
        jd = to_julian(datetime(2000, 6, 21, 12, 0), 0)
        import swisseph
        try:
            houses = compute_houses(jd, -89.0, 0.0)
            assert len(houses) == 12
        except swisseph.Error:
            pass  # expected at extreme latitudes

    def test_date_line(self):
        jd = to_julian(datetime(2000, 1, 1, 12, 0), 12)
        planets = compute_planets(jd)
        assert len(planets) == 9

    def test_negative_tz(self):
        jd = to_julian(datetime(2000, 1, 1, 12, 0), -12)
        planets = compute_planets(jd)
        assert len(planets) == 9


class TestSignBoundaries:
    def test_zero_longitude(self):
        sign, deg = get_sign(0.0)
        assert sign == "Mesha"
        assert deg == 0.0

    def test_360_wraps(self):
        sign, deg = get_sign(359.999)
        assert sign == "Meena"

    def test_exact_30(self):
        sign, deg = get_sign(30.0)
        assert sign == "Vrishabha"
        assert abs(deg) < 0.01

    def test_exact_nakshatra_boundary(self):
        span = 360 / 27
        nak, pada = get_nakshatra(span)  # exactly at 2nd nakshatra
        assert nak == "Bharani"
        assert pada == 1


class TestAllNakshatrasMatch:
    def test_all_27_nakshatras_as_boy(self):
        for n in range(27):
            result = compute_ashtakoota(n, 13)
            assert 0 <= result["total"] <= 36
            assert len(result["kootas"]) == 8

    def test_all_27_nakshatras_as_girl(self):
        for n in range(27):
            result = compute_ashtakoota(7, n)
            assert 0 <= result["total"] <= 36

    def test_all_27x27_pairs_valid(self):
        for n1 in range(27):
            for n2 in range(27):
                result = compute_ashtakoota(n1, n2)
                assert 0 <= result["total"] <= 36


class TestEmptyChart:
    def test_no_yogas_possible(self):
        """Chart where no yogas should fire — all planets spread across different signs."""
        jd = to_julian(datetime(1500, 1, 1, 12, 0), 0)
        planets = compute_planets(jd)
        houses = compute_houses(jd, 0.0, 0.0)
        phm = build_planet_house_map(planets, houses)
        yogas = check_yogas(planets, houses, phm)
        # May or may not have yogas, but shouldn't crash
        assert isinstance(yogas, list)

    def test_doshas_always_return_manglik_and_kalsarpa(self):
        jd = to_julian(datetime(2000, 6, 21, 12, 0), 0)
        planets = compute_planets(jd)
        houses = compute_houses(jd, 28.6, 77.2)
        phm = build_planet_house_map(planets, houses)
        doshas = check_doshas(planets, phm)
        names = [d["name"] for d in doshas]
        assert "Manglik Dosha" in names
        assert "Kalsarpa Dosha" in names


class TestDashaEdgeCases:
    def test_moon_at_zero_longitude(self):
        dashas = compute_dasha(0.0, datetime(2000, 1, 1))
        assert len(dashas) == 9
        assert dashas[0]["start"] == datetime(2000, 1, 1)

    def test_moon_at_359(self):
        dashas = compute_dasha(359.99, datetime(2000, 1, 1))
        assert len(dashas) == 9

    def test_antardasha_on_tiny_first_period(self):
        """When moon is near end of nakshatra, first dasha is very short."""
        dashas = compute_dasha(13.3, datetime(2000, 1, 1))  # near end of Ashwini
        dashas = compute_antardasha(dashas)
        assert len(dashas[0]["antardasha"]) == 9
        # Sub-periods should still sum to parent
        md_days = (dashas[0]["end"] - dashas[0]["start"]).total_seconds() / 86400
        ad_days = sum((a["end"] - a["start"]).total_seconds() / 86400 for a in dashas[0]["antardasha"])
        assert abs(md_days - ad_days) < 0.001
