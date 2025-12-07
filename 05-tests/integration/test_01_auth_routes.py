import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

ROOT_DIR = Path(__file__).resolve().parents[2]
API_DIR = ROOT_DIR / "01-api"

if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

from main import app

@pytest.fixture(scope="session")
def client():
    """
    Client FastAPI réel, qui utilise la vraie config de l'API
    (get_db -> Postgres via DATABASE_URL).
    Nécessite que le conteneur Postgres tourne.
    """
    with TestClient(app) as c:
        yield c

@pytest.fixture(autouse=True)
def clean_integration_data(engine):
    """
    Nettoie les données de test avant chaque test d'intégration auth.

    On supprime :
    - tous les events
    - tous les users dont l'email commence par 'integration_'
    """
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM events;"))
        conn.execute(
            text(
                "DELETE FROM users "
                "WHERE email LIKE 'integration_%@test.com';"
            )
        )

def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}

def test_health_db_ok(client):
    resp = client.get("/health/db")
    data = resp.json()
    assert resp.status_code == 200
    assert data["status"] == "ok"
    assert data["database"] == "up"

def test_register_user_ok(client):
    payload = {
        "email": "integration_user1@test.com",
        "password": "SuperSecret123",
        "display_name": "Integration User 1",
        "timezone": "Europe/Paris",
    }

    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 201, resp.text

    data = resp.json()
    assert "id" in data
    assert data["email"] == payload["email"]
    assert data["display_name"] == payload["display_name"]
    assert data["timezone"] == payload["timezone"]
    assert "password" not in data
    assert "password_hash" not in data

def test_register_same_email_fails(client):
    payload = {
        "email": "integration_duplicate@test.com",
        "password": "pwd123",
        "display_name": "Dup User",
        "timezone": "Europe/Paris",
    }

    r1 = client.post("/auth/register", json=payload)
    assert r1.status_code == 201

    r2 = client.post("/auth/register", json=payload)
    assert r2.status_code == 400

    data = r2.json()
    assert "Email déjà enregistré" in data["detail"]

def test_login_success(client):

    payload = {
        "email": "integration_login@test.com",
        "password": "MyIntegrationPwd",
        "display_name": "Login User",
        "timezone": "Europe/Paris",
    }
    r_reg = client.post("/auth/register", json=payload)
    assert r_reg.status_code == 201

    r_login = client.post(
        "/auth/login",
        json={
            "email": payload["email"],
            "password": payload["password"],
        },
    )
    assert r_login.status_code == 200, r_login.text

    data = r_login.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client):
    payload = {
        "email": "integration_wrongpwd@test.com",
        "password": "CorrectPwd123",
        "display_name": "WrongPwd User",
        "timezone": "Europe/Paris",
    }
    r_reg = client.post("/auth/register", json=payload)
    assert r_reg.status_code == 201

    r_login = client.post(
        "/auth/login",
        json={
            "email": payload["email"],
            "password": "BadPwd",
        },
    )
    assert r_login.status_code == 401
    data = r_login.json()
    assert "Email ou mot de passe incorrect" in data["detail"]

def test_login_unknown_email(client):
    r_login = client.post(
        "/auth/login",
        json={
            "email": "does_not_exist_integration@test.com",
            "password": "whatever",
        },
    )
    assert r_login.status_code == 401
    data = r_login.json()
    assert "Email ou mot de passe incorrect" in data["detail"]

def test_events_requires_auth(client):
    resp = client.get("/events")
    assert resp.status_code == 401
    assert "Aucune authentification fournie" in resp.json()["detail"]

def test_events_with_valid_token(client):
    payload = {
        "email": "integration_events@test.com",
        "password": "EventsPwd123!",
        "display_name": "Events User",
        "timezone": "Europe/Paris",
    }
    r_reg = client.post("/auth/register", json=payload)
    assert r_reg.status_code == 201

    r_login = client.post(
        "/auth/login",
        json={
            "email": payload["email"],
            "password": payload["password"],
        },
    )
    assert r_login.status_code == 200
    token = r_login.json()["access_token"]

    resp = client.get(
        "/events",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
