# 05-tests/unit/conftest.py

import pytest
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys
from pathlib import Path

# On remonte jusqu'à la racine du projet
ROOT_DIR = Path(__file__).resolve().parents[2]  # fullstack-data-application/
API_DIR = ROOT_DIR / "01-api"

if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

from models import Base # noqa: E402


# ============================================================
# PARTIE 1 — SQLite pour tests de base de données
# ============================================================

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


# ============================================================
# PARTIE 2 — Import du module d'authentification
# ============================================================

# Ajoute le dossier 04-authentication au PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parents[2]
AUTH_DIR = ROOT_DIR / "04-authentication"

if str(AUTH_DIR) not in sys.path:
    sys.path.append(str(AUTH_DIR))

# Import du module security de l’authentification
import security  # noqa: E402


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
