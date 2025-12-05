# 01-api/api/stats.py

from fastapi import APIRouter

router = APIRouter(prefix="/stats", tags=["stats"])

# plus tard : stats d'événements, temps passé, etc.
