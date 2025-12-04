# 05-tests/test_02_database.py

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app import models


def test_create_user(test_db_session: Session):
    """
    Vérifie qu'on peut créer un user avec les champs obligatoires
    et que l'ID + timestamps sont bien renseignés.
    """
    db = test_db_session

    # Arrange
    user = models.User(
        email="alexandre.videlaine@edu.esiee.fr",
        password_hash="hashed_pw",
        display_name="Alexandre VIDELAINE",
        timezone="Europe/Paris",
    )

    # Act
    db.add(user)
    db.commit()
    db.refresh(user)

    # Assert
    assert user.id is not None
    assert user.email == "alexandre.videlaine@edu.esiee.fr"
    assert user.display_name == "Alexandre VIDELAINE"
    assert user.timezone == "Europe/Paris"
    assert user.created_at is not None
    assert user.updated_at is not None


def test_create_event_for_user(test_db_session: Session):
    """
    Vérifie qu'on peut créer un event lié à un user
    et que la relation owner fonctionne.
    """
    db = test_db_session

    # Arrange : créer un user d'abord
    user = models.User(
        email="user@example.com",
        password_hash="hashed_pw",
        display_name="User Test",
        timezone="Europe/Paris",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    start = datetime(2025, 1, 10, 9, 0, tzinfo=timezone.utc)
    end = start + timedelta(hours=1)

    event = models.Event(
        user_id=user.id,
        title="Réunion Projet",
        description="Discussion sur les objectifs du sprint.",
        start_datetime=start,
        end_datetime=end,
        all_day=False,
        location="Salle 203",
        rrule=None,
        status="confirmed",
    )

    # Act
    db.add(event)
    db.commit()
    db.refresh(event)

    # Assert
    assert event.id is not None
    assert event.owner.id == user.id
    assert event.start_datetime == start
    assert event.end_datetime == end
    assert event.title == "Réunion Projet"
    assert event.status == "confirmed"
    assert event.all_day is False


def test_events_deleted_when_user_deleted(test_db_session: Session):
    """
    Vérifie que quand on supprime un user,
    ses events liés sont aussi supprimés (cascade ORM).
    """
    db = test_db_session

    # Arrange : user + event
    user = models.User(
        email="cascade@example.com",
        password_hash="pw",
        display_name="Cascade User",
        timezone="Europe/Paris",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    start = datetime.now(timezone.utc)
    end = start + timedelta(hours=2)

    event = models.Event(
        user_id=user.id,
        title="Event à supprimer",
        start_datetime=start,
        end_datetime=end,
        all_day=False,
        status="confirmed",
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    # Sanity check
    assert db.query(models.Event).count() == 1

    # Act : supprimer le user
    db.delete(user)
    db.commit()

    # Assert : plus d'events
    assert db.query(models.Event).count() == 0


def test_default_values_event(test_db_session: Session):
    """
    Vérifie les valeurs par défaut définies dans le modèle Event :
    - all_day = False
    - status = 'confirmed'
    """
    db = test_db_session

    user = models.User(
        email="defaults@example.com",
        password_hash="pw",
        display_name="Defaults User",
        timezone="Europe/Paris",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    start = datetime(2025, 2, 1, 0, 0, tzinfo=timezone.utc)
    end = start + timedelta(hours=23)

    # On ne renseigne volontairement ni all_day ni status
    event = models.Event(
        user_id=user.id,
        title="Journée Off",
        start_datetime=start,
        end_datetime=end,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    assert event.all_day is False
    assert event.status == "confirmed"
