# 01-api/routes/auth.py

import sys
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import UserCreate, UserRead, Token,LoginRequest

# --- Import du module security depuis 04-authentication ---

ROOT_DIR = Path(__file__).resolve().parents[2]
AUTH_DIR = ROOT_DIR / "04-authentication"
if str(AUTH_DIR) not in sys.path:
    sys.path.insert(0, str(AUTH_DIR))

import security  # noqa: E402  # hash_password, check_password, encode_jwt, verify_authorization_header

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
):
    # Vérifie si email déjà pris
    stmt = select(User).where(User.email == payload.email)
    existing = db.execute(stmt).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        password_hash=security.hash_password(payload.password),
        display_name=payload.display_name,
        timezone=payload.timezone or "Europe/Paris",
    )
    db.add(user)
    db.flush()  # pour avoir l'id sans commit si besoin
    db.refresh(user)

    return user

@router.post("/login", response_model=Token)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    stmt = select(User).where(User.email == payload.email)
    user = db.execute(stmt).scalar_one_or_none()

    if not user or not security.check_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = security.encode_jwt(user_id=user.id)

    return Token(access_token=access_token)
