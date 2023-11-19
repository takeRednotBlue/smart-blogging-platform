import pytest
import pytest_asyncio

from src.repository.comments import (
    create_comment,
    read_post_comment,
    remove_comment,
    update_comment,
)
from src.schemas.comments import CommentBase


@pytest.mark.asyncio
class TestCommentRepository:
    @pytest_asyncio.fixture(scope="module", autouse=True)
    async def create_post(self, client, token):
        await client.post(
            "/api/v1/posts/",
            json={"title": "test", "text": "test", "tags": ["tag1", "tag2"]},
            headers={"Authorization": f"Bearer {token}"},
        )

    async def test_create_comment(self, session, db_user):
        comment_data = {"comment": "Test comment"}
        body = CommentBase(**comment_data)
        comment = await create_comment(body, 1, db_user, session)
        assert comment.id
        assert comment.id > 0
        assert comment.comment == "Test comment"
        assert comment.user_id == db_user.id
        assert comment.post_id == 1

    async def test_read_post_comment(self, session):
        list_of_comments = await read_post_comment(1, session)
        assert isinstance(list_of_comments, list)
        assert list_of_comments[0].comment == "Test comment"

    async def test_update_comment(self, session, db_user):
        comment_data = {"comment": "Update test comment"}
        body = CommentBase(**comment_data)
        updated_comment = await update_comment(body, 1, db_user, session)
        assert updated_comment.id > 0
        assert updated_comment.comment == "Update test comment"
        assert updated_comment.user_id == db_user.id
        assert updated_comment.post_id == 1

    async def test_remove_comment(self, session):
        removed_comment = await remove_comment(1, session)
        assert removed_comment.id > 0
        assert removed_comment.comment == "Update test comment"
        assert removed_comment.post_id == 1

    async def test_remove_comment_not_found(self, session):
        removed_comment = await remove_comment(1000000, session)
        assert removed_comment is None
