# 05-tests/integration/conftest.py

import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_models import Base, User, Event


@pytest.fixture(scope="session")
def engine():
    db_url = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql+psycopg://user:postgrespassword@localhost:5432/calendar_db",
    )
    engine = create_engine(db_url)
    return engine


@pytest.fixture
def db_session(engine):
    """
    Session isolée par test avec transaction rollback.
    """
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
