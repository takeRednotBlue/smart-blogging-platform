from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException, status

from src.services.auth import auth_service


@pytest.mark.asyncio
class TestServiceAuth:
    data: dict = {
        "sub": "test@example.com",
    }

    def test_hash_and_verify_password(self):
        password = "test"
        wrong_password = "wrong"
        hashed_password = auth_service.get_password_hash(password)
        assert auth_service.verify_password(password, hashed_password)
        assert not auth_service.verify_password(wrong_password, hashed_password)
        assert password != hashed_password

    async def test_create_access_token(self):
        access_token = await auth_service.create_access_token(self.data)
        assert access_token

    async def test_create_refresh_token(self):
        refresh_token = await auth_service.create_refresh_token(self.data)
        assert refresh_token

    async def test_decode_refresh_token(self):
        refresh_token = await auth_service.create_refresh_token(self.data)
        email = await auth_service.decode_refresh_token(refresh_token)
        assert email
        assert email == self.data.get("sub")

    async def test_decode_refresh_token_wrong_scope(self):
        access_token = await auth_service.create_access_token(self.data)
        with pytest.raises(HTTPException) as excinfo:
            await auth_service.decode_refresh_token(access_token)
        assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert excinfo.value.detail == "Invalid scope for token."
        assert excinfo.type is HTTPException

    async def test_get_current_user(self, session, monkeypatch, user):
        user_data = {"sub": user.get("email")}
        access_token = await auth_service.create_access_token(user_data)
        mock_get_user_by_email = AsyncMock(return_value=user)
        monkeypatch.setattr(
            "src.repository.users.get_user_by_email",
            mock_get_user_by_email,
        )
        with patch.object(auth_service, "r") as r_mock:
            r_mock.get.return_value = None
            result_user = await auth_service.get_current_user(session, access_token)
            mock_get_user_by_email.assert_awaited_once()
            assert mock_get_user_by_email.call_count == 1
            assert user == result_user

    async def test_get_current_user_not_found(self, session, monkeypatch, user):
        user_data = {"sub": user.get("email")}
        access_token = await auth_service.create_access_token(user_data)
        mock_get_user_by_email = AsyncMock(return_value=None)
        monkeypatch.setattr(
            "src.repository.users.get_user_by_email",
            mock_get_user_by_email,
        )
        with patch.object(auth_service, "r") as r_mock:
            r_mock.get.return_value = None
            with pytest.raises(HTTPException) as excinfo:
                await auth_service.get_current_user(session, access_token)
            mock_get_user_by_email.assert_awaited_once()
            assert mock_get_user_by_email.call_count == 1
            assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert excinfo.value.detail == "Could not validate credentials."
            assert excinfo.type is HTTPException

    async def test_get_current_user_wrong_token_scope(self, session, monkeypatch, user):
        user_data = {"sub": user.get("email")}
        wrong_token = await auth_service.create_refresh_token(user_data)
        with pytest.raises(HTTPException) as excinfo:
            await auth_service.get_current_user(session, wrong_token)
        assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert excinfo.value.detail == "Could not validate credentials."
        assert excinfo.type is HTTPException

    async def test_create_email_token(self):
        token = await auth_service.create_email_token(self.data)
        assert token

    async def test_email_from_token(self):
        token = await auth_service.create_email_token(self.data)
        email = await auth_service.get_email_from_token(token)
        assert email
        assert email == self.data.get("sub")
