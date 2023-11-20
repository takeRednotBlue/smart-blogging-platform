import pytest
from unittest.mock import patch

from src.services.auth import auth_service
from src.schemas.tags import TagModel


@pytest.fixture(scope="module")
def tag_model():
    return TagModel(
        name="test_tag",
    )


@pytest.mark.asyncio
async def test_create_tag(client, token):
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = await client.post(
            "/api/v1/tags/",
            json={"name": "test_tag"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["name"] == "test_tag"
        assert "id" in data


@pytest.mark.asyncio
async def test_get_tag(client, token):
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = await client.get(
            "/api/v1/tags/test_tag",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["name"] == "test_tag"
        assert "id" in data


@pytest.mark.asyncio
async def test_get_tags(client, token):
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = await client.get(
            "/api/v1/tags/", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, list)
        assert data[0]["name"] == "test_tag"
        assert "id" in data[0]


@pytest.mark.asyncio
async def test_update_tag(client, token):
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = await client.put(
            "/api/v1/tags/test_tag",
            json={"name": "new_test_tag"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["name"] == "new_test_tag"
        assert "id" in data


@pytest.mark.asyncio
async def test_update_tag_not_found(client, token):
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = await client.put(
            "/api/v1/tags/non_existing_tag",
            json={"name": "new_test_tag"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == "Tag not found"


@pytest.mark.asyncio
async def test_delete_tag(client, token):
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = await client.delete(
            "/api/v1/tags/new_test_tag",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["name"] == "new_test_tag"
        assert "id" in data


@pytest.mark.asyncio
async def test_repeat_delete_tag(client, token):
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = await client.delete(
            "/api/v1/tags/new_test_tag",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == "Tag not found"
