"""Unit tests for kundli.match — Ashtakoota Gun Milan scoring."""
from kundli.match import compute_ashtakoota


class TestAshtakootaStructure:
    def test_returns_eight_kootas(self):
        result = compute_ashtakoota(0, 13)
        assert len(result["kootas"]) == 8

    def test_max_is_36(self):
        result = compute_ashtakoota(0, 0)
        assert result["max"] == 36

    def test_total_is_sum_of_scores(self):
        result = compute_ashtakoota(7, 21)
        assert result["total"] == sum(k["score"] for k in result["kootas"])

    def test_koota_structure(self):
        result = compute_ashtakoota(5, 18)
        for k in result["kootas"]:
            assert all(key in k for key in ["name", "description", "max", "score", "boy", "girl"])
            assert 0 <= k["score"] <= k["max"]

    def test_koota_names_in_order(self):
        result = compute_ashtakoota(0, 0)
        names = [k["name"] for k in result["kootas"]]
        assert names == ["Varna", "Vashya", "Tara", "Yoni", "Graha Maitri", "Gana", "Bhakoot", "Nadi"]

    def test_koota_max_points(self):
        result = compute_ashtakoota(0, 0)
        maxes = [k["max"] for k in result["kootas"]]
        assert maxes == [1, 2, 3, 4, 5, 6, 7, 8]


class TestAshtakootaScoring:
    def test_score_in_range(self):
        for n1 in range(0, 27, 3):
            for n2 in range(0, 27, 3):
                result = compute_ashtakoota(n1, n2)
                assert 0 <= result["total"] <= 36

    def test_same_nakshatra_nadi_dosha(self):
        # Same nakshatra always has Nadi Dosha (score 0)
        for nak in [0, 7, 13, 21, 26]:
            result = compute_ashtakoota(nak, nak)
            nadi = result["kootas"][7]
            assert nadi["score"] == 0, f"nak={nak}: expected Nadi Dosha"

    def test_same_nakshatra_max_others(self):
        # Same nakshatra should max out Varna, Vashya, Tara, Yoni, Graha Maitri, Gana, Bhakoot
        result = compute_ashtakoota(7, 7)
        for k in result["kootas"][:7]:
            assert k["score"] == k["max"], f"{k['name']} not max for same nakshatra"

    def test_different_nadi_scores_8(self):
        # Nakshatras 0 (Aadi) and 1 (Madhya) have different Nadi
        result = compute_ashtakoota(0, 1)
        nadi = result["kootas"][7]
        assert nadi["score"] == 8

    def test_reference_pair(self):
        # Shravana (21) vs Hasta (12) — verified reference
        result = compute_ashtakoota(21, 12)
        assert result["total"] == 25.0

    def test_bhakoot_favorable(self):
        # Same sign (diff=0) should score 7
        # Nakshatras 0 and 1 are both in Mesha (sign 0)
        result = compute_ashtakoota(0, 1)
        bhakoot = result["kootas"][6]
        assert bhakoot["score"] == 7

    def test_bhakoot_unfavorable(self):
        # Nakshatras in 6/8 axis should score 0
        # nak 0 -> sign 0 (Mesha), nak 14 -> sign 6 (Tula), diff=6 not in bad set
        # nak 0 -> sign 0, nak 4 -> sign 1, diff=1 which IS in bad set
        result = compute_ashtakoota(0, 4)
        bhakoot = result["kootas"][6]
        assert bhakoot["score"] == 0

    def test_tara_symmetric_max(self):
        # Same nakshatra: both tara remainders are 0 (even), so 1.5 + 1.5 = 3
        result = compute_ashtakoota(10, 10)
        tara = result["kootas"][2]
        assert tara["score"] == 3.0

    def test_all_nakshatras_valid(self):
        # Every nakshatra index 0-26 should work without error
        for n in range(27):
            result = compute_ashtakoota(n, 0)
            assert 0 <= result["total"] <= 36
            result = compute_ashtakoota(0, n)
            assert 0 <= result["total"] <= 36
