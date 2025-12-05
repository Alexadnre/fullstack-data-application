# 03-webapp/tests/conftest.py

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ajouter le répertoire parent au path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from main import app
from config import AUTH_COOKIE_NAME


@pytest.fixture
def client():
    """Client de test FastAPI."""
    return TestClient(app)


@pytest.fixture
def mock_token():
    """Token JWT de test (doit être valide selon la config)."""
    # Pour les tests, on utilisera un token réel ou mocké
    # Ici, on suppose qu'on peut créer un token valide
    import jwt
    from config import JWT_SECRET_KEY, JWT_SECRET_ALGORITHM
    
    payload = {"user_id": 1, "exp": 9999999999}  # Expiration très lointaine
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_SECRET_ALGORITHM)


@pytest.fixture
def authenticated_client(client, mock_token):
    """Client authentifié avec un token."""
    client.cookies.set(AUTH_COOKIE_NAME, mock_token)
    return client

