# 03-webapp/dependencies.py

import sys
from typing import Optional
from pathlib import Path
from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse
import jwt

from config import JWT_SECRET_KEY, JWT_SECRET_ALGORITHM, AUTH_COOKIE_NAME


def get_token_from_request(request: Request) -> Optional[str]:
    """
    Extrait le token JWT depuis le cookie de la requête.
    """
    return request.cookies.get(AUTH_COOKIE_NAME)


def decode_token(token: str) -> dict:
    """
    Décode et vérifie un token JWT.
    
    Returns:
        Payload du token (contient user_id)
    
    Raises:
        HTTPException: Si le token est invalide ou expiré
    """
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_SECRET_ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expiré.",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide.",
        )


def get_current_user(request: Request) -> int:
    """
    Dépendance FastAPI qui extrait et vérifie le token JWT.
    
    Returns:
        user_id de l'utilisateur authentifié
    
    Raises:
        HTTPException: Si non authentifié
    """
    token = get_token_from_request(request)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié.",
        )
    
    payload = decode_token(token)
    user_id = payload.get("user_id")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide: user_id manquant.",
        )
    
    return user_id


def require_auth(request: Request) -> int:
    """
    Dépendance qui redirige vers /login si non authentifié.
    Utilisée pour les routes protégées.
    """
    try:
        return get_current_user(request)
    except HTTPException as e:
        if e.status_code == 401:
            # Redirection vers login pour les requêtes HTML
            if request.headers.get("accept", "").startswith("text/html"):
                raise HTTPException(
                    status_code=status.HTTP_303_SEE_OTHER,
                    headers={"Location": "/login"},
                )
            raise
        raise

