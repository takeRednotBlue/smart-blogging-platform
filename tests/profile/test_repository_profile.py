import pytest

from src.database.models.users import User
from src.repository.profile import (
    get_profile,
    get_profile_info,
    update_profile_info,
)


@pytest.mark.asyncio
class TestProfileRepository:
    async def test_get_profile_existing_user(self, session, db_user):
        session.add(db_user)
        await session.commit()

        result = await get_profile("deadpool", session)

        assert result["username"] == "deadpool"
        assert result["email"] == "deadpool@example.com"
        assert result["description"] == "Test user"
        assert result["number_of_posts"] == 0

    async def test_get_profile_non_existing_user(self, session):
        result = await get_profile("non_existing_user", session)

        assert result is None

    async def test_get_profile_info(self, session, db_user):
        result = await get_profile_info(db_user, session)

        assert result["username"] == "deadpool"
        assert result["email"] == "deadpool@example.com"
        assert result["description"] == "Test user"

    async def test_get_profile_info_non_existing_user(self, session):
        result = await get_profile_info(
            User(username="non_existing_user"), session
        )

        assert result is None

    async def test_update_profile_info(self, session, db_user):
        new_user = db_user
        new_user.description = "Updated description"
        new_user.username = "updated_deadpool"
        result = await update_profile_info(new_user, db_user, session)

        assert result.username == "updated_deadpool"
        assert result.email == "deadpool@example.com"
        assert result.description == "Updated description"
        assert db_user.username == "updated_deadpool"

    async def test_update_profile_info_non_existing_user(self, session):
        result = await update_profile_info(
            User(username="New_user"), User(id=999999), session
        )

        assert result is None
