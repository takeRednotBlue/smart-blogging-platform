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
from src.database.models.users import Roles, User
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


@pytest_asyncio.fixture(scope="module")
async def superuser_token(client, superuser_model, session):
    with patch("src.api.auth.send_email", MagicMock()):
        await client.post(
            "/api/v1/auth/signup", json=superuser_model.model_dump()
        )
        current_user: User = (
            await session.execute(
                select(User).where(User.email == superuser_model.email)
            )
        ).scalar_one_or_none()
        current_user.confirmed = True
        current_user.roles = Roles.superuser
        session.commit()
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": superuser_model.email,
                "password": superuser_model.password,
            },
        )
        data = response.json()
        return data["access_token"]


@pytest_asyncio.fixture(scope="module")
async def moderator_token(client, moderator_user_model, session):
    with patch("src.api.auth.send_email", MagicMock()):
        await client.post(
            "/api/v1/auth/signup", json=moderator_user_model.model_dump()
        )
        current_user: User = (
            await session.execute(
                select(User).where(User.email == moderator_user_model.email)
            )
        ).scalar_one_or_none()
        current_user.confirmed = True
        current_user.roles = Roles.moderator
        session.commit()
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": moderator_user_model.email,
                "password": moderator_user_model.password,
            },
        )
        data = response.json()
        return data["access_token"]


@pytest_asyncio.fixture(scope="module")
async def admin_token(client, admin_model, session):
    with patch("src.api.auth.send_email", MagicMock()):
        await client.post("/api/v1/auth/signup", json=admin_model.model_dump())
        current_user: User = (
            await session.execute(
                select(User).where(User.email == admin_model.email)
            )
        ).scalar_one_or_none()
        current_user.confirmed = True
        current_user.roles = Roles.admin
        session.commit()
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": admin_model.email,
                "password": admin_model.password,
            },
        )
        data = response.json()
        return data["access_token"]


@pytest.fixture(scope="module")
def user():
    return {
        "username": "deadpool",
        "email": "deadpool@example.com",
        "password": "123456789",
    }


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


@pytest.fixture(scope="module")
def moderator_user_model():
    return UserModel(
        username="moderator",
        email="moderator@example.com",
        password="123456789",
    )


@pytest.fixture(scope="module")
def superuser_model():
    return UserModel(
        username="superuser",
        email="superuser@example.com",
        password="123456789",
    )


@pytest.fixture(scope="module")
def admin_model():
    return UserModel(
        username="admin",
        email="admin@example.com",
        password="123466789",
    )
