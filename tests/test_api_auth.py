from unittest.mock import AsyncMock, MagicMock

import pytest

from src.database.models.users import User
from src.repository.users import get_user_by_email


@pytest.mark.asyncio
class TestAPIAuth:
    async def test_create_user(self, client, user, monkeypatch):
        mock_send_email = MagicMock()
        monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
        respose = await client.post("api/v1/auth/signup", json=user)
        assert respose.status_code == 201, respose.text
        data = respose.json()
        assert data["user"]["email"] == user.get("email")
        assert "id" in data["user"]
        assert "created_at" in data["user"]
        assert (
            data["detail"]
            == "User successfully created. Check your email for confirmation."
        )

    async def test_repeat_create_user(self, client, user):
        respose = await client.post("api/v1/auth/signup", json=user)
        assert respose.status_code == 409, respose.text
        data = respose.json()
        assert data["detail"] == "Account already exists."

    async def test_login_user_not_confirmed(self, client, user):
        response = await client.post(
            "api/v1/auth/login",
            data={
                "username": user.get("email"),
                "password": user.get("password"),
            },
        )
        assert response.status_code == 401, response.text
        data = response.json()
        assert data["detail"] == "Email not confirmed."

    async def test_login_user(self, client, session, user):
        current_user: User = await get_user_by_email(user.get("email"), session)
        current_user.confirmed = True
        response = await client.post(
            "api/v1/auth/login",
            data={
                "username": user.get("email"),
                "password": user.get("password"),
            },
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client, user):
        response = await client.post(
            "api/v1/auth/login",
            data={"username": user.get("email"), "password": "wrong_password"},
        )
        assert response.status_code == 401, response.text
        data = response.json()
        assert data["detail"] == "Invalid password."

    async def test_login_wrong_email(self, client, user):
        response = await client.post(
            "api/v1/auth/login",
            data={"username": "wrong_email", "password": user.get("password")},
        )
        assert response.status_code == 401, response.text
        data = response.json()
        assert data["detail"] == "Invalid email."

    async def test_refresh_token(self, client, session, user):
        current_user: User = await get_user_by_email(user.get("email"), session)
        response = await client.get(
            "api/v1/auth/refresh_token",
            headers={"Authorization": f"Bearer {current_user.refresh_token}"},
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["token_type"] == "bearer"
        assert data["access_token"]
        assert data["refresh_token"]

    async def test_refresh_token_invalid(self, monkeypatch, client, user):
        monkeypatch.setattr(
            "src.services.auth.auth_service.decode_refresh_token",
            AsyncMock(return_value=user.get("email")),
        )
        response = await client.get(
            "api/v1/auth/refresh_token",
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == 401, response.text
        data = response.json()
        assert data["detail"] == "Invalid refresh token."

    async def test_confirmed_email_already_confirmed(self, monkeypatch, client, user):
        token = "valid_token"
        monkeypatch.setattr(
            "src.services.auth.auth_service.get_email_from_token",
            AsyncMock(return_value=user.get("email")),
        )
        response = await client.get(f"api/v1/auth/confirmed_email/{token}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["massage"] == "Your email is already confirmed."

    async def test_confirmed_email(self, monkeypatch, client, session, user):
        current_user: User = await get_user_by_email(user.get("email"), session)
        current_user.confirmed = False
        token = "valid_token"
        monkeypatch.setattr(
            "src.services.auth.auth_service.get_email_from_token",
            AsyncMock(return_value=user.get("email")),
        )
        monkeypatch.setattr(
            "src.repository.users.get_user_by_email",
            AsyncMock(return_value=current_user),
        )
        response = await client.get(f"api/v1/auth/confirmed_email/{token}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["massage"] == "Your email has been confirmed."

    async def test_confirmed_email_no_user(self, monkeypatch, client, session, user):
        token = "valid_token"
        monkeypatch.setattr(
            "src.services.auth.auth_service.get_email_from_token",
            AsyncMock(return_value=user.get("email")),
        )
        monkeypatch.setattr(
            "src.repository.users.get_user_by_email",
            AsyncMock(return_value=None),
        )
        response = await client.get(f"api/v1/auth/confirmed_email/{token}")
        assert response.status_code == 400, response.text
        data = response.json()
        assert data["detail"] == "Verification error."

    async def test_request_email(self, monkeypatch, client, session, user):
        current_user: User = await get_user_by_email(user.get("email"), session)
        monkeypatch.setattr(
            "src.repository.users.get_user_by_email",
            AsyncMock(return_value=current_user),
        )
        monkeypatch.setattr("src.api.auth.send_email", MagicMock())

        response = await client.post(
            "api/v1/auth/request_email", json={"email": user.get("email")}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["massage"] == "Your email is already confirmed."

    async def test_request_email_already_confirmed(
        self, monkeypatch, client, session, user
    ):
        current_user: User = await get_user_by_email(user.get("email"), session)
        current_user.confirmed = False
        monkeypatch.setattr(
            "src.repository.users.get_user_by_email",
            AsyncMock(return_value=current_user),
        )
        monkeypatch.setattr("src.api.auth.send_email", MagicMock())

        response = await client.post(
            "api/v1/auth/request_email", json={"email": user.get("email")}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["massage"] == "Check your email for confirmation."
