# tests/conftest.py
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base
from models.cultivar import Cultivar

TEST_DATABASE_URL = "sqlite:///test_embrapa.db"


@pytest.fixture(scope="session")
def test_engine():
    if os.path.exists("test_embrapa.db"):
        os.remove("test_embrapa.db")
    engine = create_engine(TEST_DATABASE_URL, connect_args={
                           "check_same_thread": False})
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()
    os.remove("test_embrapa.db")


@pytest.fixture(scope="function")
def test_session(test_engine):
    Session = sessionmaker(bind=test_engine)
    session = Session()
    yield session
    session.close()
