# 05-tests/conftest.py

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# On réutilise la Base et les modèles de ton appli
# PYTHONPATH doit contenir "01-api" quand tu lances pytest
from app.database import Base
from app import models  # import pour que les tables soient bien connues de Base


@pytest.fixture(scope="session")
def test_db_engine():
    """
    Engine de base de données pour les tests.

    Ici on utilise SQLite en mémoire :
    - ultra rapide
    - pas besoin de Docker
    - parfait pour tester les modèles SQLAlchemy
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    return engine


@pytest.fixture(scope="function")
def test_db_session(test_db_engine):
    """
    Session de base de données pour chaque test.

    Pattern setup/teardown :
    - avant le test : create_all()
    - pendant : on yield la session
    - après : on ferme la session + drop_all()

    Ça garantit :
    - isolation totale entre les tests
    - pas de pollution de données
    """
    # Création du schéma (toutes les tables connues par Base)
    Base.metadata.create_all(bind=test_db_engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_db_engine,
    )
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_db_engine)
