import time

import httpx
import pytest

from dotenv import load_dotenv
import os
load_dotenv()

API_BASE_URL = os.getenv("E2E_API_BASE_URL", "http://localhost:8000")

@pytest.fixture(scope="session")
def wait_for_api():
    """
    Attend que l'API conteneurisée réponde sur /health.
    Nécessite que `docker compose up -d` soit déjà lancé.
    """
    timeout = 15
    start = time.time()

    while time.time() - start < timeout:
        try:
            r = httpx.get(f"{API_BASE_URL}/health", timeout=2)
            if r.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(1)

    pytest.fail("API containerisée indisponible sur /health après 15s")

@pytest.mark.e2e
def test_container_health(wait_for_api):
    r = httpx.get(f"{API_BASE_URL}/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

@pytest.mark.e2e
def test_container_health_db(wait_for_api):
    r = httpx.get(f"{API_BASE_URL}/health/db")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["database"] == "up"
