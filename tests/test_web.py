"""Integration tests for web endpoints."""
import json

import pytest

from kundli.web import app

KUNDLI_FORM = {
    "date": "1996-09-23", "time": "22:17",
    "location": "Chandigarh, India", "tz": "5.5",
}
MATCH_FORM = {
    "name1": "A", "date1": "1996-09-23", "time1": "22:17",
    "location1": "Chandigarh, India", "tz1": "5.5",
    "name2": "B", "date2": "1998-03-15", "time2": "08:30",
    "location2": "Delhi, India", "tz2": "5.5",
}


@pytest.fixture()
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


@pytest.fixture()
def client_with_chart(client):
    """Client that has already generated a chart (session has chart_id)."""
    client.post("/", data=KUNDLI_FORM)
    return client


# ── GET / ────────────────────────────────────────────

class TestIndex:
    def test_status(self, client):
        assert client.get("/").status_code == 200

    def test_has_both_forms(self, client):
        body = client.get("/").data.decode()
        assert "form-kundli" in body
        assert "form-match" in body

    def test_has_tab_bar(self, client):
        body = client.get("/").data.decode()
        assert "tab-bar" in body


# ── GET /health ──────────────────────────────────────

class TestHealth:
    def test_status(self, client):
        r = client.get("/health")
        assert r.status_code == 200

    def test_json_ok(self, client):
        data = client.get("/health").get_json()
        assert data["status"] == "ok"
        assert data["ephemeris"] == "ok"


# ── POST / (kundli generation) ───────────────────────

class TestKundliGeneration:
    def test_success(self, client):
        r = client.post("/", data=KUNDLI_FORM)
        assert r.status_code == 200

    def test_has_lagna(self, client):
        body = client.post("/", data=KUNDLI_FORM).data.decode()
        assert "Vrishabha" in body

    def test_has_dasha_section(self, client):
        body = client.post("/", data=KUNDLI_FORM).data.decode()
        assert "dasha-timeline" in body

    def test_has_antardasha(self, client):
        body = client.post("/", data=KUNDLI_FORM).data.decode()
        assert "dasha-sub" in body

    def test_has_pratyantar(self, client):
        body = client.post("/", data=KUNDLI_FORM).data.decode()
        assert "dasha-prat" in body

    def test_has_section_nav(self, client):
        body = client.post("/", data=KUNDLI_FORM).data.decode()
        assert "section-nav" in body

    def test_has_view_toggle(self, client):
        body = client.post("/", data=KUNDLI_FORM).data.decode()
        assert "view-toggle" in body
        assert "btn-horoscope" in body
        assert "btn-full" in body
        assert "setView" in body

    def test_all_section_ids_present(self, client):
        body = client.post("/", data=KUNDLI_FORM).data.decode()
        for sec in ["sec-info", "sec-charts", "sec-planets", "sec-strength",
                     "sec-houses", "sec-aspects", "sec-yogas", "sec-doshas",
                     "sec-dasha", "sec-life", "sec-readings", "sec-varga", "sec-ashtakavarga"]:
            assert f'id="{sec}"' in body, f"Missing section: {sec}"

    def test_has_chat_widget(self, client):
        body = client.post("/", data=KUNDLI_FORM).data.decode()
        assert "chat-widget" in body
        assert "chat-input" in body

    def test_has_footer_actions(self, client):
        body = client.post("/", data=KUNDLI_FORM).data.decode()
        assert "btn-pdf" in body
        assert "saveChartLocally" in body
        assert "share_url" in body or "Copy Share Link" in body

    def test_has_dasha_chain_in_header(self, client):
        body = client.post("/", data=KUNDLI_FORM).data.decode()
        assert "›" in body

    def test_missing_fields(self, client):
        r = client.post("/", data={"date": "", "time": "", "location": ""})
        assert r.status_code == 200
        assert "required" in r.data.decode().lower() or "error" in r.data.decode().lower()

    def test_invalid_date(self, client):
        r = client.post("/", data={**KUNDLI_FORM, "date": "not-a-date"})
        assert r.status_code == 200
        assert "error" in r.data.decode().lower() or "invalid" in r.data.decode().lower()

    def test_invalid_tz(self, client):
        r = client.post("/", data={**KUNDLI_FORM, "tz": "999"})
        assert r.status_code == 200
        assert "error" in r.data.decode().lower() or "invalid" in r.data.decode().lower()

    def test_unknown_location(self, client):
        r = client.post("/", data={**KUNDLI_FORM, "location": "xyznonexistent12345"})
        assert r.status_code == 200
        assert "could not find" in r.data.decode().lower() or "error" in r.data.decode().lower()


# ── POST /match ──────────────────────────────────────

class TestMatch:
    def test_success(self, client):
        r = client.post("/match", data=MATCH_FORM)
        assert r.status_code == 200

    def test_has_score(self, client):
        body = client.post("/match", data=MATCH_FORM).data.decode()
        assert "/ 36" in body

    def test_has_koota_table(self, client):
        body = client.post("/match", data=MATCH_FORM).data.decode()
        assert "koota-row" in body

    def test_has_verdict(self, client):
        body = client.post("/match", data=MATCH_FORM).data.decode()
        assert "match-verdict" in body

    def test_has_people_names(self, client):
        body = client.post("/match", data=MATCH_FORM).data.decode()
        assert "A" in body and "B" in body

    def test_missing_person2(self, client):
        partial = {k: v for k, v in MATCH_FORM.items() if not k.endswith("2")}
        r = client.post("/match", data=partial)
        body = r.data.decode()
        assert "required" in body.lower() or "error" in body.lower()

    def test_error_stays_on_match_tab(self, client):
        r = client.post("/match", data={"name1": "X"})
        assert "switchTab" in r.data.decode()

    def test_default_names(self, client):
        form = {k: v for k, v in MATCH_FORM.items() if k not in ("name1", "name2")}
        body = client.post("/match", data=form).data.decode()
        assert "Person 1" in body and "Person 2" in body


# ── POST /chat ───────────────────────────────────────

class TestChat:
    def test_without_context(self, client):
        r = client.post("/chat", json={"question": "hello"})
        assert r.status_code == 200
        assert "answer" in r.get_json()

    def test_with_context(self, client_with_chart):
        r = client_with_chart.post("/chat", json={"question": "Tell me about my career"})
        assert r.status_code == 200
        data = r.get_json()
        assert len(data["answer"]) > 50

    def test_dasha_question(self, client_with_chart):
        r = client_with_chart.post("/chat", json={"question": "Tell me about my future"})
        data = r.get_json()
        assert "Mahadasha" in data["answer"]

    def test_antardasha_in_dasha_answer(self, client_with_chart):
        r = client_with_chart.post("/chat", json={"question": "Tell me about my future"})
        assert "Antardasha" in r.get_json()["answer"]

    def test_empty_question(self, client):
        r = client.post("/chat", json={"question": ""})
        assert r.status_code == 200

    def test_invalid_json(self, client):
        r = client.post("/chat", data="not json", content_type="application/json")
        assert r.status_code in (200, 400)

    def test_no_body(self, client):
        r = client.post("/chat", json=None)
        assert r.status_code in (200, 400, 415)


# ── New Routes ───────────────────────────────────────

class TestPdfDownload:
    def test_pdf_after_chart(self, client_with_chart):
        r = client_with_chart.get("/pdf")
        assert r.status_code == 200
        assert r.content_type == "application/pdf"
        assert r.data[:4] == b"%PDF"

    def test_pdf_without_chart(self, client):
        r = client.get("/pdf")
        assert r.status_code == 404

    def test_match_pdf(self, client):
        client.post("/match", data=MATCH_FORM)
        r = client.get("/match/pdf")
        assert r.status_code == 200
        assert r.data[:4] == b"%PDF"


class TestApiChart:
    def test_success(self, client):
        r = client.post("/api/chart", json={
            "date": "1996-09-23", "time": "22:17",
            "location": "Chandigarh, India", "tz": 5.5,
        })
        assert r.status_code == 200
        data = r.get_json()
        assert data["lagna"]["sign"] == "Vrishabha"
        assert len(data["planets"]) == 9
        assert len(data["houses"]) == 12
        assert len(data["dashas"]) == 9

    def test_missing_fields(self, client):
        r = client.post("/api/chart", json={"date": "1996-09-23"})
        assert r.status_code == 400

    def test_invalid_date(self, client):
        r = client.post("/api/chart", json={"date": "bad", "time": "22:17", "location": "Delhi", "tz": 5.5})
        assert r.status_code == 400


class TestShareableLink:
    def test_shareable_link(self, client):
        r = client.get("/?d=1996-09-23&t=22:17&l=Chandigarh, India&z=5.5")
        assert r.status_code == 200
        assert "Vrishabha" in r.data.decode()

    def test_shareable_link_missing_params(self, client):
        r = client.get("/?d=1996-09-23")
        # Missing time and location should show error or index
        assert r.status_code == 200


# ── Web.py coverage gaps ─────────────────────────────

class TestChartStore:
    def test_set_and_get(self, client_with_chart):
        """Chart store works via the normal flow (POST then chat reads it)."""
        r = client_with_chart.post("/chat", json={"question": "summary"})
        assert r.status_code == 200
        assert len(r.get_json()["answer"]) > 50

    def test_get_missing_key(self, client):
        """Getting a non-existent chart returns None (chat handles gracefully)."""
        with client.session_transaction() as sess:
            sess["chart_id"] = "nonexistent"
        r = client.post("/chat", json={"question": "career"})
        assert r.status_code == 200
        assert "generate a birth chart" in r.get_json()["answer"]


class TestHealthEndpoint:
    def test_health_has_chart_store(self, client):
        data = client.get("/health").get_json()
        assert "chart_store" in data


class TestMatchValidation:
    def test_invalid_date_person1(self, client):
        form = {**MATCH_FORM, "date1": "not-a-date"}
        r = client.post("/match", data=form)
        assert r.status_code == 200
        body = r.data.decode()
        assert "invalid" in body.lower() or "error" in body.lower()

    def test_invalid_location(self, client):
        form = {**MATCH_FORM, "location1": "xyznonexistent99999"}
        r = client.post("/match", data=form)
        assert r.status_code == 200
        body = r.data.decode()
        assert "could not find" in body.lower() or "error" in body.lower()


class TestApiChartErrors:
    def test_bad_location(self, client):
        r = client.post("/api/chart", json={
            "date": "1996-09-23", "time": "22:17",
            "location": "xyznonexistent99999", "tz": 5.5,
        })
        assert r.status_code == 400
        assert "could not find" in r.get_json()["error"].lower()

    def test_no_json_body(self, client):
        r = client.post("/api/chart")
        assert r.status_code in (400, 415)


class TestShareableLinks:
    def test_missing_time(self, client):
        r = client.get("/?d=1996-09-23&l=Delhi")
        assert r.status_code == 200
        body = r.data.decode()
        assert "required" in body.lower() or "error" in body.lower() or "form-kundli" in body


class TestPdfNoMatch:
    def test_match_pdf_no_session(self, client):
        r = client.get("/match/pdf")
        assert r.status_code == 404
