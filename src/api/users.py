from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

import src.repository.users as repository_users
from src.database.db import get_async_db
from src.database.models.users import Roles, User
from src.repository import ratings as repository_ratings
from src.schemas.ratings import UserRatingResponse
from src.schemas.users import RoleRequest
from src.services.auth import auth_service
from src.services.role_checker import RoleChecker

router = APIRouter(prefix="/users", tags=["users"])

# Dependencies
AsyncDBSession = Annotated[AsyncSession, Depends(get_async_db)]
RequestLimiter = Depends(RateLimiter(times=10, seconds=60))

# Allowed roles
allowed_assign_role = RoleChecker([Roles.admin, Roles.superuser])


@router.get(
    "/{user_id}/ratings",
    response_model=List[UserRatingResponse],
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
async def read_ratings_of_user(
    db: AsyncDBSession,
    user_id,
    current_user: User = Depends(auth_service.get_current_user),
) -> List[UserRatingResponse]:
    """# Get User Ratings

    ### Description
    This endpoint retrieves the ratings of a specific user.

    ### Authorization
    - Access to this endpoint requires users to be authenticated.
    - Allowed roles: "Admin", "Moderator", "User".
    - The access JWT token should be passed in the request header for authentication.

    ### Request limit
    - Maximum of 5 requests per 60 seconds.

    ### Query Parameters
    - `user_id` (**int**, required): The ID of the user.
    - `current_user` (**User**, optional): The current authenticated user. (default: None)

    ### Returns
    - `List[UserRatingResponse]`: A list of user ratings.

    ### Raises
    - `HTTPException(status_code=404)`: If the user is not found.

    ### Example
    - Get ratings of user with ID 123: [GET] `/user/123/ratings`"""
    user = await repository_ratings.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    return await repository_ratings.get_ratings_of_user(db, user_id)


@router.post(
    "/{user_id}/assign_role",
    dependencies=[RequestLimiter, Depends(allowed_assign_role)],
)
async def assign_role_to_user(
    user_id: int,
    body: RoleRequest,
    db: AsyncDBSession,
    current_user: User = Depends(auth_service.get_current_user),
):
    if current_user.roles != Roles.superuser and body.role == Roles.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superuser can assign admin role.",
        )
    user_role = await repository_users.assign_role_to_user(user_id, body, db)
    if not user_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"'{user_role.value}' role successfully assigned to user with ID {user_id}."
        },
    )
