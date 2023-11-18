import pytest
from passlib.hash import bcrypt

hashed_password = bcrypt.hash("password")


@pytest.mark.asyncio
class TestAPIProfile:
    async def test_get_profile_not_found(self, client):
        response = await client.get("/api/v1/profile/name")
        assert response.status_code == 404

    async def test_get_profile_info(self, client, db_user, token):
        response = await client.get(
            "/api/v1/profile/", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == db_user.username
        assert data["email"] == db_user.email

    async def test_get_profile(self, client, db_user):
        response = await client.get(f"/api/v1/profile/{db_user.username}")
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == db_user.username
        assert data["email"] == db_user.email

    async def test_update_profile_info(self, client, db_user, token):
        response = await client.put(
            "/api/v1/profile/",
            headers={"Authorization": f"Bearer {token}"},
            json={"username": "string", "description": "string"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "string"
        assert data["email"] == db_user.email
        assert data["description"] == "string"
