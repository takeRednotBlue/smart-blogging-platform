import asyncio
from typing import Any
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
import redis.asyncio as redis
from fastapi_limiter.depends import FastAPILimiter, RateLimiter
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from main import app
from src.conf.config import settings
from src.database.db import Base, get_async_db
from src.database.models.user import User

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
AsyncTestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


@pytest.fixture(scope="class")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="class")
async def session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    db = AsyncTestingSessionLocal()
    async with db as session:
        yield session


@pytest_asyncio.fixture(scope="class")
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


@pytest.fixture(scope="class")
def user():
    return User(username="Test", email="test@example.com", password="test")
