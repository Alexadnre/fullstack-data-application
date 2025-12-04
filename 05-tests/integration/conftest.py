import os
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

from db_models import Base, User, Event


@pytest.fixture(scope="session")
def engine():
    db_url = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql+psycopg://user:postgrespassword@localhost:5432/calendar_db",
    )

    engine = create_engine(
        db_url,
        connect_args={"connect_timeout": 2},
    )

    # Vérifie que Postgres est UP
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except OperationalError as e:
        pytest.fail(
            f"❌ Impossible de se connecter à Postgres : {e}\n"
            "➡️ Le conteneur n'est probablement pas lancé."
        )

    return engine


@pytest.fixture
def db_session(engine):
    connection = engine.connect()
    trans = connection.begin()

    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
        if trans.is_active:
            trans.rollback()
        connection.close()
