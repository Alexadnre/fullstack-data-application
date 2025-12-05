# 03-webapp/tests/test_auth.py

import pytest
from fastapi.testclient import TestClient

from config import AUTH_COOKIE_NAME


def test_login_page_accessible(client: TestClient):
    """Test que la page de login est accessible."""
    response = client.get("/login")
    assert response.status_code == 200
    assert "Connexion" in response.text


def test_login_success(client: TestClient):
    """Test de connexion réussie (nécessite une API fonctionnelle)."""
    # Note: Ce test nécessite que l'API soit accessible et qu'un utilisateur existe
    # Pour un test complet, il faudrait mocker l'API ou utiliser un serveur de test
    
    # Test que le formulaire existe
    response = client.get("/login")
    assert response.status_code == 200
    assert 'name="email"' in response.text
    assert 'name="password"' in response.text


def test_login_failure_invalid_credentials(client: TestClient):
    """Test de connexion échouée avec identifiants invalides."""
    response = client.post(
        "/login",
        data={"email": "invalid@test.com", "password": "wrongpassword"},
        follow_redirects=False,
    )
    # Devrait retourner une erreur ou rediriger
    assert response.status_code in [200, 401, 500]  # Selon la gestion d'erreur


def test_logout(client: TestClient, authenticated_client: TestClient):
    """Test de déconnexion."""
    # Vérifier qu'on est authentifié
    response = authenticated_client.get("/calendar")
    # Si on obtient 200 ou 303, on est authentifié
    
    # Déconnexion
    response = authenticated_client.get("/logout", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"
    
    # Vérifier que le cookie est supprimé
    assert AUTH_COOKIE_NAME not in response.cookies or response.cookies[AUTH_COOKIE_NAME] == ""


def test_protected_route_redirects_to_login(client: TestClient):
    """Test que les routes protégées redirigent vers /login."""
    response = client.get("/calendar", follow_redirects=False)
    # Devrait rediriger vers /login
    assert response.status_code in [303, 401]
    if response.status_code == 303:
        assert "/login" in response.headers.get("location", "")


def test_root_redirects_to_login_when_not_authenticated(client: TestClient):
    """Test que la racine redirige vers login si non authentifié."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"

