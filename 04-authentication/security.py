import base64
import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status, Header, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import User

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "CHANGE_ME")
JWT_SECRET_ALGORITHM = os.getenv("JWT_SECRET_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)

def hash_password(password: str, iterations: int = 600_000) -> str:
    """
    Hash un mot de passe en utilisant PBKDF2-HMAC-SHA256.
    Résultat sous la forme :
    pbkdf2_sha256$<iterations>$<salt_base64>$<hash_base64>
    """
    salt = os.urandom(16)

    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)

    salt_b64 = base64.b64encode(salt).decode("utf-8")
    hash_b64 = base64.b64encode(dk).decode("utf-8")

    return f"pbkdf2_sha256${iterations}${salt_b64}${hash_b64}"

def check_password(password: str, stored_hash: str) -> bool:
    """
    Vérifie qu'un mot de passe en clair correspond à un hash stocké.
    """
    try:
        algorithm, iterations, salt_b64, hash_b64 = stored_hash.split("$")
    except Exception:
        raise ValueError("Invalid hash format")

    iterations = int(iterations)
    salt = base64.b64decode(salt_b64)
    stored_dk = base64.b64decode(hash_b64)

    new_dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)

    return hmac.compare_digest(stored_dk, new_dk)

def encode_jwt(user_id: int) -> str:
    """
    Crée un JWT contenant :
    - user_id
    - exp (date d'expiration)
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "user_id": user_id,
        "exp": expire,
    }

    token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_SECRET_ALGORITHM,
    )
    return token

def decode_jwt(token: str) -> dict:
    """
    Décode un JWT et vérifie :
    - signature
    - expiration (PyJWT lèvera ExpiredSignatureError si expiré)
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
            detail="Token expired.",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
        )

def verify_authorization_header(access_token: str) -> dict:
    """
    Vérifie le header Authorization 'Bearer <token>',
    extrait le token et le décode.
    """
    if not access_token or not access_token.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No auth provided.",
        )

    token = access_token.split("Bearer ")[1]
    payload = decode_jwt(token)
    return payload

def get_current_user(authorization: str = Header(None, alias="Authorization"), db: Session = Depends(get_db)) -> User:
    """
    Dépendance FastAPI qui récupère l'utilisateur courant depuis le header
    Authorization: Bearer <token> et le DB session.
    Renvoie une instance `User` ou lève HTTPException 401.
    """
    payload = verify_authorization_header(authorization)
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user
