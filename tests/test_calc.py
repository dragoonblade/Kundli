"""Unit tests for kundli.calc — planetary positions, dasha, antardasha, yogas."""
from datetime import datetime, timedelta

from kundli.calc import (
    get_sign, get_nakshatra, to_julian,
    compute_planets, compute_houses, compute_dasha,
    compute_antardasha, compute_pratyantar,
    compute_aspects, check_yogas, build_planet_house_map,
    compute_divisional_chart,
    SIGNS, NAKSHATRAS, DASHA_ORDER, DASHA_YEARS, DASHA_TOTAL_YEARS,
    EXALTATION, OWN_SIGNS,
)

# Reference birth: 23 Sep 1996, 22:17, Chandigarh (30.734, 76.793), TZ +5.5
BIRTH = datetime(1996, 9, 23, 22, 17)
TZ = 5.5
LAT, LON = 30.7340, 76.7930
JD = to_julian(BIRTH, TZ)
PLANETS = compute_planets(JD)
HOUSES = compute_houses(JD, LAT, LON)


class TestConstants:
    def test_signs_count(self):
        assert len(SIGNS) == 12

    def test_nakshatras_count(self):
        assert len(NAKSHATRAS) == 27

    def test_dasha_order_count(self):
        assert len(DASHA_ORDER) == 9

    def test_dasha_total_years(self):
        assert DASHA_TOTAL_YEARS == 120
        assert sum(DASHA_YEARS.values()) == 120


class TestGetSign:
    def test_first_sign(self):
        assert get_sign(0.0) == ("Mesha", 0.0)

    def test_mid_sign(self):
        sign, deg = get_sign(45.0)
        assert sign == "Vrishabha"
        assert abs(deg - 15.0) < 0.01

    def test_last_sign(self):
        sign, deg = get_sign(359.99)
        assert sign == "Meena"

    def test_boundary(self):
        assert get_sign(30.0)[0] == "Vrishabha"
        assert get_sign(29.99)[0] == "Mesha"


class TestGetNakshatra:
    def test_first_nakshatra(self):
        nak, pada = get_nakshatra(0.0)
        assert nak == "Ashwini"
        assert pada == 1

    def test_pada_progression(self):
        span = 360 / 27
        _, pada1 = get_nakshatra(0.1)
        _, pada2 = get_nakshatra(span / 4 + 0.1)
        _, pada3 = get_nakshatra(span / 2 + 0.1)
        _, pada4 = get_nakshatra(3 * span / 4 + 0.1)
        assert [pada1, pada2, pada3, pada4] == [1, 2, 3, 4]


class TestToJulian:
    def test_known_value(self):
        jd = to_julian(BIRTH, TZ)
        assert abs(jd - 2450350.1993) < 0.001

    def test_different_tz(self):
        jd_ist = to_julian(BIRTH, 5.5)
        jd_utc = to_julian(BIRTH, 0.0)
        # Higher TZ offset means earlier UT, so smaller JD
        assert jd_ist < jd_utc


class TestComputePlanets:
    def test_planet_count(self):
        assert len(PLANETS) == 9

    def test_all_planets_present(self):
        names = {p["planet"] for p in PLANETS}
        expected = {"Surya", "Chandra", "Mangal", "Budh", "Guru", "Shukra", "Shani", "Rahu", "Ketu"}
        assert names == expected

    def test_planet_structure(self):
        for p in PLANETS:
            assert all(k in p for k in ["planet", "longitude", "sign", "degree", "nakshatra", "pada", "retrograde"])
            assert 0 <= p["longitude"] < 360
            assert 0 <= p["degree"] < 30
            assert p["sign"] in SIGNS
            assert p["nakshatra"] in NAKSHATRAS
            assert p["pada"] in (1, 2, 3, 4)

    def test_reference_moon(self):
        moon = next(p for p in PLANETS if p["planet"] == "Chandra")
        assert moon["sign"] == "Makara"
        assert moon["nakshatra"] == "Shravana"
        assert abs(moon["longitude"] - 290.27) < 0.1

    def test_reference_lagna(self):
        assert HOUSES[0]["sign"] == "Vrishabha"

    def test_rahu_ketu_opposition(self):
        rahu = next(p for p in PLANETS if p["planet"] == "Rahu")
        ketu = next(p for p in PLANETS if p["planet"] == "Ketu")
        diff = abs(rahu["longitude"] - ketu["longitude"])
        assert abs(diff - 180) < 0.01

    def test_retrograde_detection(self):
        budh = next(p for p in PLANETS if p["planet"] == "Budh")
        assert budh["retrograde"] is True  # Mercury retrograde on this date
        surya = next(p for p in PLANETS if p["planet"] == "Surya")
        assert surya["retrograde"] is False  # Sun never retrograde


class TestComputeHouses:
    def test_house_count(self):
        assert len(HOUSES) == 12

    def test_house_structure(self):
        for h in HOUSES:
            assert all(k in h for k in ["house", "sign", "degree"])
            assert 1 <= h["house"] <= 12
            assert h["sign"] in SIGNS
            assert 0 <= h["degree"] < 30

    def test_house_numbers_sequential(self):
        assert [h["house"] for h in HOUSES] == list(range(1, 13))


class TestComputeDasha:
    def setup_method(self):
        moon = next(p for p in PLANETS if p["planet"] == "Chandra")
        self.dashas = compute_dasha(moon["longitude"], BIRTH)

    def test_nine_periods(self):
        assert len(self.dashas) == 9

    def test_starts_at_birth(self):
        assert self.dashas[0]["start"] == BIRTH

    def test_contiguous(self):
        for i in range(8):
            gap = abs((self.dashas[i]["end"] - self.dashas[i + 1]["start"]).total_seconds())
            assert gap < 1

    def test_first_lord_matches_nakshatra(self):
        moon = next(p for p in PLANETS if p["planet"] == "Chandra")
        nak_idx = int(moon["longitude"] // (360 / 27))
        from kundli.calc import NAKSHATRA_LORDS
        expected = NAKSHATRA_LORDS[nak_idx % 9]
        assert self.dashas[0]["lord"] == expected

    def test_all_lords_in_order(self):
        first_idx = DASHA_ORDER.index(self.dashas[0]["lord"])
        for i, d in enumerate(self.dashas):
            assert d["lord"] == DASHA_ORDER[(first_idx + i) % 9]

    def test_dasha_structure(self):
        for d in self.dashas:
            assert all(k in d for k in ["lord", "start", "end", "years"])
            assert d["lord"] in DASHA_ORDER
            assert d["end"] > d["start"]
            assert d["years"] > 0

    def test_reference_current_dasha(self):
        # In March 2026, should be in Guru Mahadasha (Jan 2024 - Jan 2040)
        guru = next(d for d in self.dashas if d["lord"] == "Guru")
        assert guru["years"] == 16
        assert guru["start"].year == 2024


class TestComputeAntardasha:
    def setup_method(self):
        moon = next(p for p in PLANETS if p["planet"] == "Chandra")
        self.dashas = compute_antardasha(compute_dasha(moon["longitude"], BIRTH))

    def test_nine_sub_periods_each(self):
        for d in self.dashas:
            assert len(d["antardasha"]) == 9

    def test_first_sub_matches_parent(self):
        for d in self.dashas:
            assert d["antardasha"][0]["lord"] == d["lord"]

    def test_sub_periods_sum_to_parent(self):
        for d in self.dashas:
            md_days = (d["end"] - d["start"]).total_seconds() / 86400
            ad_days = sum((a["end"] - a["start"]).total_seconds() / 86400 for a in d["antardasha"])
            assert abs(md_days - ad_days) < 0.001

    def test_sub_periods_contiguous(self):
        for d in self.dashas:
            for i in range(8):
                gap = abs((d["antardasha"][i]["end"] - d["antardasha"][i + 1]["start"]).total_seconds())
                assert gap < 1

    def test_proportional_duration(self):
        # For a full-length dasha, each antardasha should be proportional
        d = next(d for d in self.dashas if d["years"] == DASHA_YEARS[d["lord"]])
        for ad in d["antardasha"]:
            expected_frac = DASHA_YEARS[ad["lord"]] / DASHA_TOTAL_YEARS
            actual_frac = (ad["end"] - ad["start"]).total_seconds() / (d["end"] - d["start"]).total_seconds()
            assert abs(expected_frac - actual_frac) < 0.001


class TestComputePratyantar:
    def setup_method(self):
        moon = next(p for p in PLANETS if p["planet"] == "Chandra")
        self.dashas = compute_pratyantar(compute_antardasha(compute_dasha(moon["longitude"], BIRTH)))

    def test_nine_sub_sub_periods_each(self):
        for d in self.dashas:
            for ad in d["antardasha"]:
                assert len(ad["pratyantar"]) == 9

    def test_sub_sub_periods_sum_to_parent(self):
        for d in self.dashas:
            for ad in d["antardasha"]:
                ad_days = (ad["end"] - ad["start"]).total_seconds() / 86400
                pr_days = sum((p["end"] - p["start"]).total_seconds() / 86400 for p in ad["pratyantar"])
                assert abs(ad_days - pr_days) < 0.001

    def test_total_count(self):
        count = sum(len(ad["pratyantar"]) for d in self.dashas for ad in d["antardasha"])
        assert count == 9 * 9 * 9  # 729


class TestComputeAspects:
    def test_returns_list(self):
        aspects = compute_aspects(PLANETS)
        assert isinstance(aspects, list)

    def test_aspect_structure(self):
        for a in compute_aspects(PLANETS):
            assert all(k in a for k in ["from", "to", "aspect_house", "target_sign"])
            assert a["from"] in {p["planet"] for p in PLANETS}
            assert a["target_sign"] in SIGNS

    def test_no_self_aspect(self):
        for a in compute_aspects(PLANETS):
            assert a["from"] not in a["to"]


class TestCheckYogas:
    def test_without_houses(self):
        result = check_yogas(PLANETS)
        assert isinstance(result, list)
        for y in result:
            assert "name" in y and "desc" in y

    def test_with_houses_superset(self):
        without = check_yogas(PLANETS)
        with_h = check_yogas(PLANETS, HOUSES)
        assert len(with_h) >= len(without)

    def test_panch_mahapurusha_detection(self):
        # Guru in Dhanu (own sign) with Lagna in Dhanu (kendra)
        planets = [{"planet": p, "sign": "Mesha", "longitude": 10.0} for p in
                   ["Surya", "Chandra", "Mangal", "Budh", "Shukra", "Shani", "Rahu", "Ketu"]]
        planets.append({"planet": "Guru", "sign": "Dhanu", "longitude": 250.0})
        houses = [{"house": 1, "sign": "Dhanu", "degree": 5.0}]
        yogas = check_yogas(planets, houses)
        names = {y["name"] for y in yogas}
        assert "Hamsa" in names

    def test_kemadruma_detection(self):
        # All planets in same sign as Moon — no adjacent planets
        planets = [{"planet": p, "sign": "Mesha", "longitude": 10.0}
                   for p in ["Surya", "Chandra", "Mangal", "Budh", "Guru", "Shukra", "Shani", "Rahu", "Ketu"]]
        yogas = check_yogas(planets)
        names = {y["name"] for y in yogas}
        assert "Kemadruma" in names

    def test_no_kemadruma_with_adjacent(self):
        # Planet adjacent to Moon should prevent Kemadruma
        planets = [
            {"planet": "Chandra", "sign": "Mesha", "longitude": 10.0},
            {"planet": "Mangal", "sign": "Vrishabha", "longitude": 40.0},  # adjacent
        ] + [{"planet": p, "sign": "Simha", "longitude": 130.0}
             for p in ["Surya", "Budh", "Guru", "Shukra", "Shani", "Rahu", "Ketu"]]
        yogas = check_yogas(planets)
        names = {y["name"] for y in yogas}
        assert "Kemadruma" not in names


class TestBuildPlanetHouseMap:
    def test_all_planets_mapped(self):
        phm = build_planet_house_map(PLANETS, HOUSES)
        assert len(phm) == 9
        for p in PLANETS:
            assert p["planet"] in phm
            assert 1 <= phm[p["planet"]] <= 12


class TestDivisionalCharts:
    def test_navamsa(self):
        d9 = compute_divisional_chart(PLANETS, 9)
        assert len(d9) == 9
        for p in d9:
            assert p["sign"] in SIGNS
            assert 0 <= p["degree"] < 30

    def test_all_divisions(self):
        for div in [2, 3, 4, 6, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60]:
            result = compute_divisional_chart(PLANETS, div)
            assert len(result) == 9
