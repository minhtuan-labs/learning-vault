import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set TESTING before importing database module
os.environ["TESTING"] = "true"

from app.database import Base, get_db
from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def db_engine():
    """Create test database."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(db_engine):
    """Create test session."""
    TestingSessionLocal = sessionmaker(bind=db_engine)
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def client(db_session):
    """Create test client."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
