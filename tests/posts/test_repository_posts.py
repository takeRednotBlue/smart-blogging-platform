import pytest
import pytest_asyncio

from src.repository.posts import (
    create_post,
    get_posts,
    get_post,
    update_post,
    remove_post,
    get_or_create_tag,
)
from src.schemas.posts import PostCreate, PostUpdate
from sqlalchemy import select
from src.database.models.users import User


@pytest.mark.asyncio
class TestPostsRepository:
    @pytest_asyncio.fixture(scope="module", autouse=True)
    async def con_post(self, client, token):
        await client.post(
            "/api/v1/posts/",
            json={"title": "test5", "text": "test", "tags": ["tag1", "tag2"]},
            headers={"Authorization": f"Bearer {token}"},
        )

    async def test_create_post(self, session, db_user):
        post_data = {"title": "test5", "text": "test", "tags": ["tag1", "tag2"]}
        body = PostCreate(**post_data)
        post = await create_post(body, db_user, session)
        assert post.id
        assert post.id > 0
        assert post.title == "test5"
        assert post.user_id == db_user.id
        assert len(post.tags) == 2

    async def test_get_or_create_tag(self, session):
        tag_name = "tag1"
        tag = await get_or_create_tag(tag_name, session)
        assert tag.name == tag_name  # Проверяем, что имя совпадает
        assert tag.id is not None
        existing_tag = await get_or_create_tag(tag_name, session)
        assert existing_tag.id == tag.id

    async def test_get_posts(self, session):
        posts = await get_posts(session)
        assert len(posts) > 0

    async def test_get_post(self, session):
        post = await get_post(1, session)
        assert post.title == "test5"

    async def test_update_post(self, session, user):
        stmt = select(User).where(User.username == user.get("username"))
        fetch_user = (await session.execute(stmt)).scalars().first()
        post_data = {"title": "test6", "text": "testhoho", "tags": ["testtag1", "testtag2"]}
        body = PostUpdate(**post_data)
        updated_post = await update_post(1, fetch_user, body, session)
        assert updated_post.title == "test6"
        assert updated_post.text == "testhoho"
        assert updated_post.user_id == fetch_user.id
        assert updated_post.tags[0].name == "testtag1"
        assert updated_post.tags[1].name == "testtag2"
        assert len(updated_post.tags) == 2

    async def test_delete_post(self, session, user):
        stmt = select(User).where(User.username == user.get("username"))
        fetch_user = (await session.execute(stmt)).scalars().first()
        post = await remove_post(1, fetch_user, session)
        assert post is not None
        assert post.id == 1
