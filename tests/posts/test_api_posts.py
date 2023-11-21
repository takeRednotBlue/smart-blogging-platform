import pytest
import pytest_asyncio


@pytest.mark.asyncio
class TestPosts:
    @pytest_asyncio.fixture(scope="module", autouse=True)
    async def con_post(self, client, token):
        await client.post(
            "/api/v1/posts/",
            json={
                "title": "testtitle",
                "text": "testtext",
                "tags": ["tag1", "tag2"],
            },
            headers={"Authorization": f"Bearer {token}"},
        )

    async def test_create_post(self, client, token):
        response = await client.post(
            "/api/v1/posts/",
            json={"title": "test5", "text": "test", "tags": ["tag1", "tag2"]},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["title"] == "test5"
        assert "id" in data

    async def test_read_posts(self, client):
        response = await client.get("/api/v1/posts/")
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) > 0

    async def test_read_post(self, client):
        response = await client.get("/api/v1/posts/1")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["title"] == "testtitle"

    async def test_update_post(self, client, token):
        response = await client.put(
            "/api/v1/posts/1",
            json={"title": "test6", "text": "testhoho", "tags": ["testtag1", "testtag2"]},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["title"] == "test6"

    async def test_remove_post(self, client, token):
        response = await client.delete(
            "/api/v1/posts/1", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
