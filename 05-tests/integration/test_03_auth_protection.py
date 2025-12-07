import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[2]
API_DIR = ROOT_DIR / "01-api"

if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

from main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


def _register_and_login(client, email="integration_auth@test.com"):
    payload = {
        "email": email,
        "password": "IntegrationAuthPwd123!",
        "display_name": "Auth User",
        "timezone": "Europe/Paris",
    }
    r_reg = client.post("/auth/register", json=payload)
    assert r_reg.status_code == 201, r_reg.text

    r_login = client.post(
        "/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    assert r_login.status_code == 200, r_login.text
    return r_login.json()["access_token"]


def test_events_requires_auth_header(client):
    resp = client.get("/events")
    assert resp.status_code == 401
    assert "Aucune authentification fournie" in resp.json()["detail"]


def test_events_rejects_non_bearer_prefix(client):
    resp = client.get("/events", headers={"Authorization": "Token abc"})
    assert resp.status_code == 401
    assert "Aucune authentification fournie" in resp.json()["detail"]


def test_events_rejects_invalid_token(client):
    resp = client.get(
        "/events",
        headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.invalid"},
    )
    assert resp.status_code == 401
    assert "Jeton invalide" in resp.json()["detail"]


def test_get_event_not_found_returns_404(client):
    token = _register_and_login(client, email="integration_auth_404@test.com")
    resp = client.get("/events/999999", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404
    assert "Évènement introuvable" in resp.json()["detail"]


def test_create_event_without_auth_returns_401(client):
    payload = {
        "title": "NoAuthEvent",
        "start_datetime": "2025-01-01T09:00:00Z",
        "end_datetime": "2025-01-01T10:00:00Z",
        "all_day": False,
    }
    resp = client.post("/events", json=payload)
    assert resp.status_code == 401
    assert "Aucune authentification fournie" in resp.json()["detail"]
