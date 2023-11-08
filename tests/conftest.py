import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from src.database.db import get_async_db
from src.database.db import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


def base_session():
    """Base generator to be used in creating fixtures for pytest
    and for setUp in unittest TesCase classes

    :yield: Session object for db connection
    :rtype: Generator[Session, Any, None]
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def session():
    # Create the database for pytest tests
    yield next(base_session())


@pytest.fixture(scope="module")
def client(session):
    # Dependency override

    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_async_db] = override_get_db

    yield TestClient(app)


@pytest.fixture(scope="module")
def user():
    return {
        "username": "deadpool",
        "email": "deadpool@example.com",
        "password": "123456789",
    }
