import logging
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio

from src.database.models.users import Roles

logger = logging.getLogger("BaseLogger")


@pytest.mark.asyncio
class TestComments:
    @pytest_asyncio.fixture(scope="module", autouse=True)
    async def create_post(self, client, token):
        await client.post(
            "/api/v1/posts/",
            json={"title": "test", "text": "test", "tags": ["tag1", "tag2"]},
            headers={"Authorization": f"Bearer {token}"},
        )

    async def test_create_comment(self, client, token):
        response = await client.post(
            "/api/v1/posts/1/comments",
            json={
                "comment": "test comment",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["comment"] == "test comment"
        assert "id" in data

    async def test_read_post_comments_successful(self, client):
        response = await client.get("/api/v1/posts/1/comments")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data[0]["comment"] == "test comment"

    async def test_read_post_comments_fail(self, client):
        response = await client.get("/api/v1/posts/100/comments")
        assert response.status_code == 404, response.text

    async def test_update_comment(self, client, token):
        response = await client.put(
            "/api/v1/posts/1/comments/1",
            json={
                "comment": "updated comment",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200, response.text

    async def test_update_comment_fail(self, client, token):
        response = await client.put(
            "/api/v1/posts/1/comments/100",
            json={
                "comment": "updated comment",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404, response.text

    async def test_remove_comment(self, client, moderator_token):
        response = await client.delete(
            "/api/v1/posts/1/comments/1",
            headers={"Authorization": f"Bearer {moderator_token}"},
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["message"] == "Comment successfully deleted"
        assert data["deleted_comment_id"] == 1
        assert data["deleted_comment"] == "updated comment"

    async def test_remove_comment_not_permitted(self, client, token):
        response = await client.delete(
            "/api/v1/posts/1/comments/1",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403, response.text
        data = response.json()
        assert data["detail"] == "Operation not permitted"

    async def test_remove_comment_fail(self, client, moderator_token):
        response = await client.delete(
            "/api/v1/posts/1/comments/100",
            headers={"Authorization": f"Bearer {moderator_token}"},
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == "Comment not found"
