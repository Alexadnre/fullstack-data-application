# 01-api/api/users.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserRead])
def get_users(db: Session = Depends(get_db)):
    """
    Liste tous les utilisateurs.
    """
    users = db.query(User).all()
    return users
