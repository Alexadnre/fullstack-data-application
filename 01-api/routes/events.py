from fastapi import APIRouter, HTTPException, Depends
import sys
from pathlib import Path

# Assure l'accès au module d'authentification (même technique que dans `auth.py`)
ROOT_DIR = Path(__file__).resolve().parents[2]
AUTH_DIR = ROOT_DIR / "04-authentication"
if str(AUTH_DIR) not in sys.path:
    sys.path.insert(0, str(AUTH_DIR))

import security  # noqa: E402  # get_current_user
from sqlalchemy.orm import Session

from schemas import EventCreate, EventUpdate, EventRead
from database import get_db
from models import Event, User

router = APIRouter(prefix="/events", tags=["events"])


# -------------------------
# GET /events
# -------------------------
@router.get("/", response_model=list[EventRead])
def get_events(db: Session = Depends(get_db), current_user: User = Depends(security.get_current_user)):
    """Retourne uniquement les événements appartenant à l'utilisateur courant."""
    events = db.query(Event).filter(Event.user_id == current_user.id).all()
    return events


# -------------------------
# GET /events/{id}
# -------------------------
@router.get("/{event_id}", response_model=EventRead)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(404, "Event not found")
    return event


# -------------------------
# POST /events
# -------------------------
@router.post("/", response_model=EventRead)
def create_event(payload: EventCreate, db: Session = Depends(get_db)):
    event = Event(**payload.dict())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


# -------------------------
# PUT /events/{id}
# -------------------------
@router.put("/{event_id}", response_model=EventRead)
def update_event(event_id: int, payload: EventUpdate, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(404, "Event not found")

    for key, value in payload.dict(exclude_unset=True).items():
        setattr(event, key, value)

    db.commit()
    db.refresh(event)
    return event


# -------------------------
# DELETE /events/{id}
# -------------------------
@router.delete("/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(404, "Event not found")

    db.delete(event)
    db.commit()
    return {"message": "Event deleted"}
