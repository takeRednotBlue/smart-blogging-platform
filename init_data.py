import asyncio

from src.conf.config import settings
from src.database.db import async_session_maker
from src.database.models.users import Roles, User
from src.schemas.users import UserModel
from src.services.auth import auth_service
import src.repository.users as repo_users

user_models: list[UserModel] = [
    {
        "model": UserModel(
            username=settings.superuser_username,
            email=settings.superuser_email,
            password=auth_service.get_password_hash(
                settings.superuser_password
            ),
        ),
        "role": Roles.superuser,
    },
    {
        "model": UserModel(
            username="test_user",
            email="user@example.com",
            password=auth_service.get_password_hash("test_user"),
        ),
        "role": Roles.user,
    },
]


async def init_users():
    async with async_session_maker() as db:
        for user in user_models:
            db_user = await repo_users.get_user_by_email(
                user.get("model").email, db
            )
            if not db_user:
                user = User(
                    **user.get("model").model_dump(),
                    confirmed=True,
                    roles=user.get("role"),
                )
                db.add(user)
        await db.commit()


if __name__ == "__main__":
    asyncio.run(init_users())
