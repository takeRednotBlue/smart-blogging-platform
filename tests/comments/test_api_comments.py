import pytest


@pytest.mark.asyncio
class TestComments:
    async def test_create_post(self, client):
        response = await client.post("/api/posts/")
        assert response.status_code == 201

    async def test_create_comment(self, client):
        response = await client.post(
            "/api/posts/1/comments",
            json={
                "comment": "test comment",
            },
        )
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["comment"] == "test comment"
        assert "id" in data

    async def test_read_post_comments_successful(self, client):
        response = await client.get("/api/posts/1/comments")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data[0]["comment"] == "test comment"

    async def test_read_post_comments_fail(self, client):
        response = await client.get("/api/posts/100/comments")
        assert response.status_code == 404, response.text

    async def test_update_comment(self, client):
        response = await client.put(
            "/api/posts/1/comments/1",
            json={
                "comment": "updated comment",
            },
        )
        assert response.status_code == 200, response.text

    async def test_update_comment_fail(self, client):
        response = await client.put(
            "/api/posts/1/comments/100",
            json={
                "comment": "updated comment",
            },
        )
        assert response.status_code == 404, response.text

    async def test_remove_comment(self, client):
        response = await client.delete("/api/posts/1/comments/1")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["message"] == "Comment successfully deleted"
        assert data["deleted_comment_id"] == 1
        assert data["deleted_comment"] == "updated comment"

    async def test_remove_comment_fail(self, client):
        response = await client.delete("/api/posts/1/comments/100")
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == "Comment not found"
