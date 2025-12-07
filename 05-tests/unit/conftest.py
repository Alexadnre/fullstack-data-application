import pytest
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
API_DIR = ROOT_DIR / "01-api"

if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

from models import Base

ENGINE = create_engine("sqlite:///:memory:", future=True)
TestingSessionLocal = sessionmaker(bind=ENGINE, autoflush=False, autocommit=False)

@pytest.fixture(scope="function")
def db_session():
    """
    Crée une base temporaire SQLite pour chaque test.
    """
    Base.metadata.create_all(bind=ENGINE)

    session = TestingSessionLocal()
    try:
        yield session
        session.commit()
    finally:
        session.close()
        Base.metadata.drop_all(bind=ENGINE)

ROOT_DIR = Path(__file__).resolve().parents[2]
AUTH_DIR = ROOT_DIR / "04-authentication"

if str(AUTH_DIR) not in sys.path:
    sys.path.append(str(AUTH_DIR))

import security

@pytest.fixture(scope="session")
def auth_security():
    """
    Fixture qui expose le module security pour tous les tests.
    """
    return security

@pytest.fixture
def sample_password():
    """
    Mot de passe générique utilisé dans plusieurs tests.
    """
    return "mon_super_mdp"
