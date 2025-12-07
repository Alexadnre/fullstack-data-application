from fastapi import APIRouter, HTTPException, Depends
import sys
from pathlib import Path

from sqlalchemy.orm import Session

ROOT_DIR = Path(__file__).resolve().parents[2]
AUTH_DIR = ROOT_DIR / "04-authentication"
if str(AUTH_DIR) not in sys.path:
    sys.path.insert(0, str(AUTH_DIR))

import security

from schemas import EventCreate, EventUpdate, EventRead
from database import get_db
from models import Event, User

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/", response_model=list[EventRead])
def get_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """Retourne uniquement les événements appartenant à l'utilisateur courant."""
    events = db.query(Event).filter(Event.user_id == current_user.id).all()
    return events

@router.get("/{event_id}", response_model=EventRead)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    event = (
        db.query(Event)
        .filter(Event.id == event_id, Event.user_id == current_user.id)
        .first()
    )
    if not event:
        raise HTTPException(404, "Évènement introuvable")
    return event

@router.post("/", response_model=EventRead)
def create_event(
    payload: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):

    event = Event(**payload.dict(), user_id=current_user.id)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

@router.put("/{event_id}", response_model=EventRead)
def update_event(
    event_id: int,
    payload: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    event = (
        db.query(Event)
        .filter(Event.id == event_id, Event.user_id == current_user.id)
        .first()
    )
    if not event:
        raise HTTPException(404, "Évènement introuvable")

    for key, value in payload.dict(exclude_unset=True).items():
        setattr(event, key, value)

    db.commit()
    db.refresh(event)
    return event

@router.delete("/{event_id}")
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    event = (
        db.query(Event)
        .filter(Event.id == event_id, Event.user_id == current_user.id)
        .first()
    )
    if not event:
        raise HTTPException(404, "Évènement introuvable")

    db.delete(event)
    db.commit()
    return {"message": "Event deleted"}
