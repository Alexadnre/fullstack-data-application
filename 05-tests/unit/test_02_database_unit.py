from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
API_DIR = ROOT_DIR / "01-api"

if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

from models import User, Event

@pytest.mark.unit
def test_create_user_ok(db_session: Session):
    """Test de création d’un utilisateur valide (modèle User)."""
    db = db_session

    user = User(
        email="alex@example.com",
        password_hash="hashed_pw",
        display_name="Alex",
        timezone="Europe/Paris",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    assert user.id is not None
    assert user.email == "alex@example.com"
    assert user.display_name == "Alex"
    assert user.timezone == "Europe/Paris"
    assert user.created_at is not None
    assert user.updated_at is not None

@pytest.mark.unit
def test_email_unique_constraint(db_session: Session):
    """Test de la contrainte d’unicité sur l’email (IntegrityError attendue)."""
    db = db_session

    user1 = User(
        email="dup@test.com",
        password_hash="pw1",
        display_name="User1",
        timezone="Europe/Paris",
    )
    user2 = User(
        email="dup@test.com",
        password_hash="pw2",
        display_name="User2",
        timezone="Europe/Paris",
    )

    db.add(user1)
    db.commit()

    db.add(user2)

    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()

@pytest.mark.unit
def test_create_event_for_user(db_session: Session):
    """Test de création d’un event lié à un utilisateur (relation User → Event)."""
    db = db_session

    user = User(
        email="user@test.com",
        password_hash="pw",
        display_name="UserTest",
        timezone="Europe/Paris",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    start = datetime(2025, 1, 10, 9, 0, tzinfo=timezone.utc)
    end = start + timedelta(hours=1)

    event = Event(
        user_id=user.id,
        title="Réunion Projet",
        description="Sprint planning",
        start_datetime=start,
        end_datetime=end,
        all_day=False,
        status="confirmed",
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    assert event.id is not None
    assert event.owner.id == user.id
    assert event.title == "Réunion Projet"

    assert event.start_datetime == start.replace(tzinfo=None)
    assert event.end_datetime == end.replace(tzinfo=None)

    assert event.all_day is False
    assert event.status == "confirmed"

@pytest.mark.unit
def test_events_deleted_on_user_delete(db_session: Session):
    """Supprimer un user doit supprimer ses events (cascade ORM delete-orphan)."""
    db = db_session

    user = User(
        email="cascade@test.com",
        password_hash="pw",
        display_name="Cascade",
        timezone="Europe/Paris",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    start = datetime.now(timezone.utc)
    end = start + timedelta(hours=1)

    event = Event(
        user_id=user.id,
        title="Event supprimé",
        start_datetime=start,
        end_datetime=end,
    )
    db.add(event)
    db.commit()

    assert db.query(Event).count() == 1

    db.delete(user)
    db.commit()

    assert db.query(Event).count() == 0

@pytest.mark.unit
def test_event_default_values(db_session: Session):
    """Test des valeurs par défaut du modèle Event (status, all_day)."""
    db = db_session

    user = User(
        email="default@test.com",
        password_hash="pw",
        display_name="DefaultUser",
        timezone="Europe/Paris",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    start = datetime(2025, 2, 1, 12, 0, tzinfo=timezone.utc)
    end = start + timedelta(hours=2)

    event = Event(
        user_id=user.id,
        title="Journée off",
        start_datetime=start,
        end_datetime=end,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    assert event.all_day is False
    assert event.status == "confirmed"
