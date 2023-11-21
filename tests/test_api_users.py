import pytest
from pytest_lazyfixture import lazy_fixture


@pytest.mark.asyncio
class TestAPIUsers:
    async def test_assing_role_to_user(self, client, superuser_token):
        response = await client.post(
            "/api/v1/users/1/assign_role",
            headers={"Authorization": f"Bearer {superuser_token}"},
            json={"role": "admin"},
        )

        data = response.json()
        assert response.status_code == 200
        assert (
            data["message"]
            == "'admin' role successfully assigned to user with ID 1."
        )

    @pytest.mark.parametrize(
        "test_token,role,detail",
        [
            (
                lazy_fixture("admin_token"),
                "admin",
                "Only superuser can assign admin role.",
            ),
            (
                lazy_fixture("moderator_token"),
                "admin",
                "Operation not permitted",
            ),
        ],
    )
    async def test_assing_admin_role_to_user_wrong_role(
        self, test_token, role, detail, client
    ):
        response = await client.post(
            "/api/v1/users/1/assign_role",
            headers={"Authorization": f"Bearer {test_token}"},
            json={"role": role},
        )

        data = response.json()
        assert response.status_code == 403
        assert data["detail"] == detail

    async def test_assing_role_to_user_wrong_user(
        self, client, superuser_token
    ):
        response = await client.post(
            "/api/v1/users/99/assign_role",
            headers={"Authorization": f"Bearer {superuser_token}"},
            json={"role": "admin"},
        )

        data = response.json()
        assert response.status_code == 404
        assert data["detail"] == "User not found."
