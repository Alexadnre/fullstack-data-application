# 05-tests\conftest.py

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from unit.db_models import Base

# SQLite in-memory pour les tests
ENGINE = create_engine("sqlite:///:memory:", future=True)

TestingSessionLocal = sessionmaker(bind=ENGINE, autoflush=False, autocommit=False)

@pytest.fixture(scope="function")
def db_session():
    """
    Crée une base temporaire pour chaque test.
    """
    Base.metadata.create_all(bind=ENGINE)

    session = TestingSessionLocal()
    try:
        yield session
        session.commit()
    finally:
        session.close()
        Base.metadata.drop_all(bind=ENGINE)
