# 01-api/api/users.py

from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])

# à remplir plus tard si tu fais des routes admin
