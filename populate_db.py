import asyncio

import src.repository.comments as repo_comments
import src.repository.posts as repo_posts
import src.repository.ratings as repo_ratings
import src.repository.users as repo_users
from src.conf.config import settings
from src.database.db import async_session_maker
from src.database.models.users import Roles, User
from src.schemas.comments import CommentBase
from src.schemas.posts import PostCreate
from src.schemas.ratings import RatingModel
from src.schemas.users import UserModel
from src.services.auth import auth_service

comments: list[CommentBase] = [
    CommentBase(comment="Amazing!"),
    CommentBase(comment="You are the best!"),
    CommentBase(comment="Disgusting how can you write such nonsense!"),
    CommentBase(comment="Don't listen to haters at all, do what you want!"),
    CommentBase(comment="I'm calling police, fed up with idiots!"),
]

posts: list[PostCreate] = [
    PostCreate(
        title="Is python an animal or its lifestyle?",
        text="Python is an animal. It has no friends.",
        tags=["python", "animal", "lifestyle", "programming"],
    ),
    PostCreate(
        title="Why Python?",
        text="Because it's fun and easy.",
        tags=["python", "programming", "mood"],
    ),
    PostCreate(
        title="Why biogoose exists and how do they help us?",
        text="Biogoose scares orks and they eat them.",
        tags=["animal", "weapon", "biohazard", "freedom"],
    ),
    PostCreate(
        title="Do alembic sucks?",
        text="Yes, it does.",
        tags=["alembic", "sucks", "python", "programming"],
    ),
]

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
    {
        "model": UserModel(
            username="best_user",
            email="best_user@example.com",
            password=auth_service.get_password_hash("best_user"),
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


async def add_posts():
    async with async_session_maker() as db:
        user = await repo_users.get_user_by_email("best_user@example.com", db)
        for post in posts:
            await repo_posts.create_post(post, user, db)


async def add_comments():
    async with async_session_maker() as db:
        user = await repo_users.get_user_by_email("user@example.com", db)
        for comment in comments:
            await repo_comments.create_comment(comment, 2, user, db)


async def add_ratings():
    async with async_session_maker() as db:
        user = await repo_users.get_user_by_email("user@example.com", db)
        await repo_ratings.add_rating_for_post(
            db, RatingModel(rating_type="LIKE", user_id=user.id), 2
        )


async def main():
    await init_users()
    await add_posts()
    await add_comments()
    await add_ratings()


if __name__ == "__main__":
    asyncio.run(main())
