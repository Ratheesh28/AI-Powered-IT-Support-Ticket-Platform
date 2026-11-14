import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.predictor import predictor
from app.preprocessing import CATEGORIES


def test_health_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "model_loaded": True, "database": "ok"}


def test_health_degraded_when_model_missing(client, monkeypatch):
    monkeypatch.setattr(predictor, "pipeline", None)
    r = client.get("/health")
    assert r.status_code == 503
    assert r.json()["status"] == "degraded"
    assert r.json()["model_loaded"] is False


# ---------- /predict ----------

def test_predict_returns_structured_json(client, valid_ticket):
    r = client.post("/predict", json=valid_ticket)
    assert r.status_code == 200
    body = r.json()
    assert body["category"] in CATEGORIES
    assert 0.0 <= body["confidence"] <= 1.0
    assert set(body["probabilities"]) == set(CATEGORIES)
    assert sum(body["probabilities"].values()) == pytest.approx(1.0, abs=0.01)
    assert body["confidence"] == max(body["probabilities"].values())


def test_predict_does_not_save(client, valid_ticket):
    client.post("/predict", json=valid_ticket)
    assert client.get("/tickets").json()["total"] == 0


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"title": "Only a title"},
        {"description": "Only a description with enough length"},
        {"title": "x", "description": "too short"},
        {"title": "   ", "description": "A perfectly long description here"},
        {"title": "Valid title", "description": "d" * 5001},
        {"title": 123, "description": ["not", "a", "string"]},
    ],
)
def test_predict_rejects_invalid_input(client, payload):
    r = client.post("/predict", json=payload)
    assert r.status_code == 422
    assert "detail" in r.json()


def test_predict_rejects_text_with_no_usable_words(client):
    r = client.post("/predict", json={"title": "!!!", "description": "??????????"})
    assert r.status_code == 422
    assert "usable words" in r.json()["detail"]


def test_predict_returns_503_when_model_missing(client, valid_ticket, monkeypatch):
    monkeypatch.setattr(predictor, "pipeline", None)
    r = client.post("/predict", json=valid_ticket)
    assert r.status_code == 503
    assert "not loaded" in r.json()["detail"]


def test_unexpected_errors_return_generic_500(valid_ticket, monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("secret internal detail")

    monkeypatch.setattr(predictor, "predict", boom)
    with TestClient(app, raise_server_exceptions=False) as c:
        r = c.post("/predict", json=valid_ticket)
    assert r.status_code == 500
    assert r.json() == {"detail": "Internal server error."}  # internals are not leaked


# ---------- /tickets ----------

def test_create_ticket_saves_prediction(client, valid_ticket):
    r = client.post("/tickets", json=valid_ticket)
    assert r.status_code == 201
    body = r.json()
    assert body["id"] == 1
    assert body["title"] == valid_ticket["title"]
    assert body["predicted_category"] in CATEGORIES
    assert 0.0 <= body["confidence"] <= 1.0
    assert "created_at" in body


def test_create_ticket_trims_whitespace(client):
    r = client.post(
        "/tickets",
        json={"title": "  Wifi down  ", "description": "   No internet connection at all   "},
    )
    assert r.status_code == 201
    assert r.json()["title"] == "Wifi down"
    assert r.json()["description"] == "No internet connection at all"


def test_create_ticket_invalid_input_saves_nothing(client):
    assert client.post("/tickets", json={"title": "x"}).status_code == 422
    assert client.get("/tickets").json()["total"] == 0


def test_list_tickets_newest_first(client, valid_ticket):
    for i in range(3):
        client.post("/tickets", json={**valid_ticket, "title": f"Ticket number {i}"})
    body = client.get("/tickets").json()
    assert body["total"] == 3
    assert [t["title"] for t in body["items"]] == [
        "Ticket number 2",
        "Ticket number 1",
        "Ticket number 0",
    ]


def test_list_tickets_pagination(client, valid_ticket):
    for i in range(5):
        client.post("/tickets", json={**valid_ticket, "title": f"Ticket number {i}"})
    page = client.get("/tickets", params={"limit": 2, "offset": 2}).json()
    assert page["total"] == 5
    assert page["limit"] == 2 and page["offset"] == 2
    assert [t["title"] for t in page["items"]] == ["Ticket number 2", "Ticket number 1"]


@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 101}, {"offset": -1}])
def test_list_tickets_rejects_bad_pagination(client, params):
    assert client.get("/tickets", params=params).status_code == 422


def test_list_tickets_category_filter(client):
    client.post("/tickets", json={
        "title": "Password reset",
        "description": "I forgot my password and my account is locked",
    })
    client.post("/tickets", json={
        "title": "Printer broken",
        "description": "Paper jam and the printer tray shows an error",
    })
    body = client.get("/tickets", params={"category": "Account Access"}).json()
    assert body["total"] == 1
    assert body["items"][0]["predicted_category"] == "Account Access"


def test_list_tickets_unknown_category(client):
    r = client.get("/tickets", params={"category": "Bogus"})
    assert r.status_code == 422
    assert "Unknown category" in r.json()["detail"]


# ---------- /analytics ----------

def test_analytics_with_no_tickets(client):
    body = client.get("/analytics").json()
    assert body["total_tickets"] == 0
    assert body["tickets_by_category"] == {c: 0 for c in CATEGORIES}
    assert body["average_confidence"] is None
    # real test-set metrics saved by train.py are exposed, not invented
    assert 0.0 <= body["model_metrics"]["accuracy"] <= 1.0
    assert "SYNTHETIC_DEMO" in body["model_metrics"]["dataset_note"]


def test_analytics_counts_saved_tickets(client, valid_ticket):
    ids = [client.post("/tickets", json=valid_ticket).json() for _ in range(3)]
    body = client.get("/analytics").json()
    assert body["total_tickets"] == 3
    assert sum(body["tickets_by_category"].values()) == 3
    expected_avg = sum(t["confidence"] for t in ids) / 3
    assert body["average_confidence"] == pytest.approx(expected_avg, abs=1e-3)


# ---------- CORS ----------

def test_cors_allows_configured_origin(client):
    r = client.options(
        "/predict",
        headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST"},
    )
    assert r.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_cors_blocks_unknown_origin(client):
    r = client.options(
        "/predict",
        headers={"Origin": "http://evil.example", "Access-Control-Request-Method": "POST"},
    )
    assert "access-control-allow-origin" not in r.headers
