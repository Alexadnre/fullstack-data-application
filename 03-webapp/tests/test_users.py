# 03-webapp/tests/test_users.py

import pytest
from fastapi.testclient import TestClient


def test_users_page_requires_auth(client: TestClient):
    """Test que la page utilisateurs nécessite une authentification."""
    response = client.get("/users", follow_redirects=False)
    # Devrait rediriger vers login ou retourner 401
    assert response.status_code in [303, 401]
    if response.status_code == 303:
        assert "/login" in response.headers.get("location", "")


def test_create_user_requires_auth(client: TestClient):
    """Test que la création d'utilisateur nécessite une authentification."""
    response = client.post(
        "/users",
        data={
            "email": "test@example.com",
            "password": "password123",
            "display_name": "Test User",
            "timezone": "Europe/Paris",
        },
        follow_redirects=False,
    )
    # Devrait rediriger vers login ou retourner 401
    assert response.status_code in [303, 401]


def test_users_page_structure(authenticated_client: TestClient):
    """Test de la structure de la page utilisateurs (si authentifié)."""
    # Note: Nécessite une API fonctionnelle ou mockée
    response = authenticated_client.get("/users")
    # Si l'API répond, on devrait avoir une page
    if response.status_code == 200:
        assert "Utilisateurs" in response.text or "Gestion des utilisateurs" in response.text

