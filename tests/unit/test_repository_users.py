import pytest
from sqlalchemy import select

from src.database.models.users import User
from src.repository.users import (
    confirmed_email,
    create_user,
    get_user_by_email,
    update_token,
)


@pytest.mark.asyncio
class TestRepositoryUsers:
    async def test_create_user(self, user_model, session):
        created_user = await create_user(user_model, session)
        assert isinstance(created_user, User)
        assert hasattr(created_user, "id")
        assert created_user.username == user_model.username
        assert created_user.email == user_model.email
        assert created_user.password == user_model.password
        assert created_user.created_at
        assert not created_user.confirmed
        assert created_user.refresh_token is None

    async def test_get_user_by_email(self, user_model, session):
        user = await get_user_by_email(user_model.email, session)
        assert isinstance(user, User)
        assert user.username == user_model.username
        assert user.email == user_model.email
        assert user.password == user_model.password

    async def test_get_user_by_email_wrong(self, user_model, session):
        user = await get_user_by_email("wrong_email", session)
        assert user is None

    async def test_update_token(self, user_model, session):
        test_token = "test"
        user = (
            await session.execute(
                select(User).where(User.email == user_model.email)
            )
        ).scalar_one_or_none()
        await update_token(user, test_token, session)
        await session.refresh(user)
        assert user.refresh_token == test_token

    async def test_confirmed_email(self, user_model, session):
        user = (
            await session.execute(
                select(User).where(User.email == user_model.email)
            )
        ).scalar_one_or_none()
        await confirmed_email(user.email, session)
        await session.refresh(user)
        assert user.confirmed
