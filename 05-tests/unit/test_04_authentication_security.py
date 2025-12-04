# 05-tests/unit/test_04_authentication_security.py

from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi import HTTPException


# -------------------------------------------------------------------
# Tests hash_password / check_password
# -------------------------------------------------------------------


def test_hash_password_format(auth_security, sample_password):
    """
    Le hash doit respecter le format :
    pbkdf2_sha256$<iterations>$<salt>$<hash>
    """
    hashed = auth_security.hash_password(sample_password)

    parts = hashed.split("$")
    assert len(parts) == 4
    assert parts[0] == "pbkdf2_sha256"
    assert parts[1].isdigit()
    assert parts[2]  # salt non vide
    assert parts[3]  # hash non vide


def test_check_password_ok(auth_security, sample_password):
    """
    check_password doit retourner True avec le bon mot de passe.
    """
    hashed = auth_security.hash_password(sample_password)
    assert auth_security.check_password(sample_password, hashed) is True


def test_check_password_wrong(auth_security, sample_password):
    """
    check_password doit retourner False avec un mauvais mot de passe.
    """
    hashed = auth_security.hash_password(sample_password)
    assert auth_security.check_password("mauvais_mdp", hashed) is False


def test_check_password_invalid_format_raises(auth_security):
    """
    check_password doit lever ValueError si le format du hash est invalide.
    """
    with pytest.raises(ValueError):
        auth_security.check_password("whatever", "format_invalide")


# -------------------------------------------------------------------
# Tests encode_jwt / decode_jwt
# -------------------------------------------------------------------


def test_encode_and_decode_jwt_ok(auth_security):
    """
    encode_jwt + decode_jwt doivent permettre de retrouver le user_id
    et inclure un champ exp.
    """
    user_id = 123
    token = auth_security.encode_jwt(user_id=user_id)

    payload = auth_security.decode_jwt(token)
    assert payload.get("user_id") == user_id
    assert "exp" in payload


def test_decode_jwt_expired_raises_http_exception(auth_security):
    """
    Un token expiré doit provoquer une HTTPException 401 'Token expired.'.
    """
    now = datetime.now(timezone.utc)
    expired_time = now - timedelta(minutes=1)

    payload = {
        "user_id": 999,
        "exp": expired_time,
    }

    token = jwt.encode(
        payload,
        auth_security.JWT_SECRET_KEY,
        algorithm=auth_security.JWT_SECRET_ALGORITHM,
    )

    with pytest.raises(HTTPException) as exc_info:
        auth_security.decode_jwt(token)

    exc = exc_info.value
    assert exc.status_code == 401
    assert "Token expired" in exc.detail


def test_decode_jwt_invalid_token_raises_http_exception(auth_security):
    """
    Un token totalement invalide doit lever HTTPException 401 'Invalid token.'.
    """
    invalid_token = "this.is.not.a.valid.jwt"

    with pytest.raises(HTTPException) as exc_info:
        auth_security.decode_jwt(invalid_token)

    exc = exc_info.value
    assert exc.status_code == 401
    assert "Invalid token" in exc.detail


# -------------------------------------------------------------------
# Tests verify_authorization_header
# -------------------------------------------------------------------


def test_verify_authorization_header_ok(auth_security):
    """
    Un header 'Bearer <token>' valide doit renvoyer le payload décodé.
    """
    user_id = 42
    token = auth_security.encode_jwt(user_id=user_id)
    header = f"Bearer {token}"

    payload = auth_security.verify_authorization_header(header)
    assert payload.get("user_id") == user_id


def test_verify_authorization_header_missing_prefix_raises(auth_security):
    """
    Si le header ne commence pas par 'Bearer ', on doit avoir 401 'No auth provided.'.
    """
    token = auth_security.encode_jwt(user_id=1)
    header = token  # pas de 'Bearer '

    with pytest.raises(HTTPException) as exc_info:
        auth_security.verify_authorization_header(header)

    exc = exc_info.value
    assert exc.status_code == 401
    assert "No auth provided" in exc.detail


def test_verify_authorization_header_empty_raises(auth_security):
    """
    Header vide → 401 'No auth provided.'.
    """
    with pytest.raises(HTTPException) as exc_info:
        auth_security.verify_authorization_header("")

    exc = exc_info.value
    assert exc.status_code == 401
    assert "No auth provided" in exc.detail
