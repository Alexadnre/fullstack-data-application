from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from ..schemas.events import EventCreate, EventUpdate, EventOut
from ..database import get_db
from ..models import Event

router = APIRouter(prefix="/events", tags=["events"])


# -------------------------
# GET /events
# -------------------------
@router.get("/", response_model=list[EventOut])
def get_events(db: Session = Depends(get_db)):
    events = db.query(Event).all()
    return events


# -------------------------
# GET /events/{id}
# -------------------------
@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(404, "Event not found")
    return event


# -------------------------
# POST /events
# -------------------------
@router.post("/", response_model=EventOut)
def create_event(payload: EventCreate, db: Session = Depends(get_db)):
    event = Event(**payload.dict())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


# -------------------------
# PUT /events/{id}
# -------------------------
@router.put("/{event_id}", response_model=EventOut)
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
