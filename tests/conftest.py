import asyncio

import pytest
import pytest_asyncio
import redis.asyncio as redis
from fastapi_limiter.depends import FastAPILimiter
from httpx import AsyncClient
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from main import app
from src.database.db import Base, get_async_db
from src.schemas.users import UserModel
from src.conf.config import settings
from src.database.models.user import User

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
AsyncTestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()



@pytest_asyncio.fixture(scope="module")
async def session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    db = AsyncTestingSessionLocal()
    async with db as session:
        yield session


@pytest.fixture(scope="module")
def sync_client():
    return TestClient(app)

@pytest_asyncio.fixture(scope="module")
async def client(session):
    # Dependency override
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_async_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as client:
        r = await redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=0,
            encoding="utf-8",
            decode_responses=True,
        )
        await FastAPILimiter.init(r)


    async with AsyncClient(app=app, base_url="http://test") as client:
        r = await redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=0,
            encoding="utf-8",
            decode_responses=True,
        )
        await FastAPILimiter.init(r)
        
        yield client


@pytest.fixture(scope="class")
def db_user():
    return User(username="Test", email="test@example.com", password="test")

@pytest.fixture(scope="class")
def user():
    return {
        "username": "deadpool",
        "email": "deadpool@example.com",
        "password": "123456789",
    }


@pytest.fixture(scope="module")
def user_model():
    return UserModel(
        username="deadpool",
        email="deadpool@example.com",
        password="123456789",
    )
