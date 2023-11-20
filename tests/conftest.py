import asyncio
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio
import redis.asyncio as redis
from fastapi.testclient import TestClient
from fastapi_limiter.depends import FastAPILimiter
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from main import app
from src.conf.config import settings
from src.database.db import Base, get_async_db
from src.database.models.users import User
from src.schemas.users import UserModel

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
AsyncTestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
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
        yield client


@pytest_asyncio.fixture(scope="module")
async def token(client, user, session):
    with patch("src.api.auth.send_email", MagicMock()):
        await client.post("/api/v1/auth/signup", json=user)
        current_user: User = (
            await session.execute(
                select(User).where(User.email == user.get("email"))
            )
        ).scalar_one_or_none()
        current_user.confirmed = True
        session.commit()
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": user.get("email"),
                "password": user.get("password"),
            },
        )
        data = response.json()
        return data["access_token"]


@pytest.fixture(scope="module")
def db_user():
    return User(
        username="deadpool",
        email="deadpool@example.com",
        password="123456789",
        confirmed=True,
        description="Test user",
    )


@pytest.fixture(scope="module")
def user_model():
    return UserModel(
        username="deadpool",
        email="deadpool@example.com",
        password="123456789",
    )


@pytest_asyncio.fixture
async def token(client, db_user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.services.email.send_email", mock_send_email)
    await client.post(
        "/api/v1/auth/signup",
        json={
            "username": db_user.username,
            "email": db_user.email,
            "password": db_user.password,
        },
    )
    current_user: User = (
        await session.execute(select(User).where(User.email == db_user.email))
    ).scalar_one_or_none()
    current_user.confirmed = True
    await session.commit()
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": db_user.email, "password": db_user.password},
    )
    data = response.json()
    return data["access_token"]
