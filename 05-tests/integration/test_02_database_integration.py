# 05-tests/integration/test_02_database_integration.py

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from db_models import User, Event


def test_tables_exist(engine):
    """
    Vérifie que le conteneur Postgres a bien exécuté calendar_schema.sql
    et créé les tables 'users' et 'events'.
    """
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname='public';")
        )
        tables = {row[0] for row in result}

    assert "users" in tables
    assert "events" in tables


def test_seed_users_exist(db_session):
    """
    Vérifie qu'il y a au moins un utilisateur seedé par calendar_seed.sql
    (si tu seeds des users).
    """
    users = db_session.query(User).all()
    assert len(users) >= 1


def test_insert_user_and_event(db_session):
    """
    Teste l'insertion d'un user + event dans le Postgres réel.
    """
    from datetime import datetime, timezone

    # Insertion user
    user = User(
        email="integration-test@example.com",
        password_hash="hash",
        display_name="Integration Test User",
    )
    db_session.add(user)
    db_session.flush()

    # Insertion event
    event = Event(
        user_id=user.id,
        title="Integration Event",
        description="Créé depuis un test",
        start_datetime=datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc),
        end_datetime=datetime(2025, 1, 1, 11, 0, tzinfo=timezone.utc),
        all_day=False,
        status="confirmed",
    )
    db_session.add(event)
    db_session.commit()

    # Vérification
    fetched = (
        db_session.query(Event)
        .filter_by(user_id=user.id, title="Integration Event")
        .one()
    )
    assert fetched.description == "Créé depuis un test"


def test_fk_constraint(db_session):
    """
    Vérifie que la contrainte de clé étrangère (user_id FK users.id)
    empêche de créer un event pour un user inexistant.
    """
    from datetime import datetime, timezone

    bad_event = Event(
        user_id=999999,
        title="Should Fail",
        start_datetime=datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc),
        end_datetime=datetime(2025, 1, 1, 11, 0, tzinfo=timezone.utc),
        all_day=False,
        status="confirmed",
    )

    db_session.add(bad_event)

    # Pas de rollback manuel ici : la fixture s’en charge
    with pytest.raises(IntegrityError):
        db_session.commit()
