from time import sleep

import pytest
import pytest_asyncio
from unittest.mock import MagicMock, patch
from sqlalchemy import select

from src.database.models.users import User
from src.database.models.rating import Post
from src.services.auth import auth_service
from src.schemas.ratings import PostModel
from src.schemas.users import UserModel


@pytest_asyncio.fixture
async def token(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.services.email.send_email", mock_send_email)
    await client.post("/api/v1/auth/signup", json=user)
    current_user: User = (await session.execute(select(User).where(User.email == user.get('email')))).scalar_one_or_none()
    current_user.confirmed = True
    session.commit()
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    data = response.json()
    return data["access_token"]


@pytest_asyncio.fixture
async def create_post(session):
    new_post = Post(user_id=1)
    session.add(new_post)
    await session.commit()
    await session.refresh(new_post)
    return new_post


@pytest_asyncio.fixture
async def user2(session):
    new_user = User(username="test_user2", email="test_user2@test.com", password = "test1234")
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


@pytest_asyncio.fixture
async def user3(session): 
    new_user = User(username="test_user3", email="test_user3@test.com", password = "test1234")
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


@pytest.mark.asyncio
async def test_create_rating(client, token, create_post, user2):
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = await client.post(
            "/api/v1/post/1/ratings",
            json={
                "type": "LIKE",
                "user_id": 2
                },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201, response.text
        data =  response.json()
        assert "id" in data


@pytest.mark.asyncio
async def test_create_rating_to_not_existing_post(client, token):
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = await client.post(
            "/api/v1/post/2/ratings",
            json={
                "type": "LIKE",
                "user_id": 1
                },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text


@pytest.mark.asyncio
async def test_create_rating_with_not_existing_user(client, token):
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = await client.post(
            "/api/v1/post/1/ratings",
            json={
                "type": "LIKE",
                "user_id": 4
                },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text


@pytest.mark.asyncio
async def test_create_rating_to_own_post(client, token):
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = await client.post(
            "/api/v1/post/1/ratings",
            json={
                "type": "LIKE",
                "user_id": 1
                },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 400, response.text


@pytest.mark.asyncio
async def test_create_rating_to_already_estimated_post(client, token, user3):
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = await client.post(
            "/api/v1/post/1/ratings",
            json={
                "type": "LIKE",
                "user_id": 2
                },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 400, response.text


@pytest.mark.asyncio
async def test_read_rating_of_post(client, token):
    sleep(60)
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        await client.post(
            "/api/v1/post/1/ratings",
            json={
                "type": "LIKE",
                "user_id": 3
                },
            headers={"Authorization": f"Bearer {token}"}
        )
        response = await client.get(
            "/api/v1/post/1/rating",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data =  response.json()
        assert data == 2


@pytest.mark.asyncio
async def test_read_ratings_of_post(client, token):
    
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None

        response = await client.get(
            "/api/v1/post/1/ratings",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200, response.text
        data =  response.json()
        assert data == [{'id': 1, 'type': 'LIKE', 'user_id': 2}, {'id': 2, 'type': 'LIKE', 'user_id': 3}]


@pytest.mark.asyncio
async def test_read_ratings_of_non_existing_post(client, token):
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None

        response = await client.get(
            "/api/v1/post/2/ratings",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404, response.text


@pytest.mark.asyncio
async def test_read_ratings_of_user(client, token, create_post):
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None

        response = await client.get(
            "/api/v1/user/3/ratings",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200, response.text
        data =  response.json()
        assert data == [{'id': 2, 'type': 'LIKE', 'post_id': 1}]


@pytest.mark.asyncio
async def test_read_ratings_of_non_user(client, token, create_post):
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None

        response = await client.get(
            "/api/v1/user/4/ratings",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
       

@pytest.mark.asyncio
async def test_remove_rating_for_post(client, token):
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None

        response = await client.delete(
            "/api/v1/post/1/ratings/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text


@pytest.mark.asyncio
async def test_remove_rating_for_non_existing_post(client, token):
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None

        response = await client.delete(
            "/api/v1/post/2/ratings/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text


@pytest.mark.asyncio
async def test_remove_rating_for_non_existing_rating(client, token):
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None

        response = await client.delete(
            "/api/v1/post/1/ratings/10",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text