# 01-api/api/events.py

from fastapi import APIRouter

router = APIRouter(prefix="/events", tags=["events"])

# plus tard : GET /events, POST /events, etc.
