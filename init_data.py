import asyncio

from src.conf.config import settings
from src.database.db import async_session_maker
from src.database.models.users import Roles, User
from src.schemas.users import UserModel
from src.services.auth import auth_service

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
        users = [
            User(
                **user.get("model").model_dump(),
                confirmed=True,
                roles=user.get("role"),
            )
            for user in user_models
        ]
        db.add_all(users)
        await db.commit()


if __name__ == "__main__":
    asyncio.run(init_users())
