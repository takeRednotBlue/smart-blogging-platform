from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import settings
import src.repository.profile as repository_profile
from src.database.db import get_async_db
from src.database.models.users import User
from src.schemas.profiles import Profile, ProfileInfoResponse, ProfileResponse
from src.schemas.users import UserUpdate, UserAvatarUpdate
from src.services.auth import auth_service
from src.services.cloudinarry import round_profile_pic

router = APIRouter(prefix="/profile", tags=["profile"])

# Dependencies
RequestLimiter = Depends(RateLimiter(times=10, seconds=60))
AsyncDBSession = Annotated[AsyncSession, Depends(get_async_db)]
AuthCurrentUser = Annotated[User, Depends(auth_service.get_current_user)]


@router.get("/", response_model=ProfileInfoResponse)
async def get_profile_info(db: AsyncDBSession, current_user: AuthCurrentUser):
    """# Get Profile Info

    ### Description
    This endpoint retrieves the profile information for the authenticated user.

    ### Authorization
    - Access to this endpoint requires users to be authenticated.
    - Allowed roles: "Admin", "Moderator", "User".
    - The access JWT token should be passed in the request header for authentication.

    ### Request limit
    - No limit

    ### Query Parameters
    None.

    ### Returns
    - `User`: The profile information for the authenticated user.

    ### Raises
    - `HTTPException(status_code=404)`: If the user is not found.

    ### Example
    - Get profile info: [GET] `api/v1/profile/`"""
    user = await repository_profile.get_profile_info(current_user, db)
    return user


@router.put(
    "/",
    response_model=Profile,
    dependencies=[RequestLimiter],
)
async def update_profile_info(
    body: UserUpdate,
    db: AsyncDBSession,
    current_user: AuthCurrentUser,
):
    """# Update Profile Info

    ### Description
    This endpoint is used to update the profile information of a user.

    ### Authorization
    - Access to this endpoint requires users to be authenticated.
    - Allowed roles: "Admin", "Moderator", "User".
    - The access JWT token should be passed in the request header for authentication.

    ### Request limit
    - Maximum 3 requests per 60 seconds.

    ### Query Parameters
    - `body` (**UserUpdate**, required): The updated profile information of the user.

    ### Returns
    - `User`: The updated user profile information.

    ### Raises
    - `HTTPException(status_code=status.HTTP_404_NOT_FOUND)`: If the user is not found.

    ### Example
    - Update profile info: [PUT] `api/v1/profile/`"""
    user = await repository_profile.update_profile_info(body, current_user, db)

    return user

@router.put(
    "/avatar",
    response_model=Profile,
    dependencies=[RequestLimiter],
)
async def update_avatar(
    body: UserAvatarUpdate,
    db: AsyncDBSession,
    current_user: AuthCurrentUser,
):
    """# Update Profile Info

    ### Description
    This endpoint is used to update the profile information of a user.

    ### Authorization
    - Access to this endpoint requires users to be authenticated.
    - Allowed roles: "Admin", "Moderator", "User".
    - The access JWT token should be passed in the request header for authentication.

    ### Request limit
    - Maximum 3 requests per 60 seconds.

    ### Query Parameters
    - `body` (**UserAvatarUpdate**, required): The updated profile information of the user.

    ### Returns
    - `User`: The updated user profile information.

    ### Raises
    - `HTTPException(status_code=status.HTTP_404_NOT_FOUND)`: If the user is not found.

    ### Example
    - Update profile info: [PUT] `api/v1/profile/`"""
    draft=body.avatar
    result = await round_profile_pic(current_user.id, draft)
    url, round_url = result['original'], result['round']
    user = await repository_profile.update_avatar(url, round_url, current_user, db)

    return user

@router.get("/{username}", response_model=ProfileResponse)
async def get_profile(db: AsyncDBSession, username: str):
    """# Get Profile

    ### Description
    This endpoint retrieves the profile information of a user based on their username.

    ### Authorization
    - Allowed roles: "Admin", "Moderator", "User".

    ### Request limit
    - No limit.

    ### Query Parameters
    - `username` (**str**, required): The username of the user.

    ### Returns
    - `User`: The profile information of the user.

    ### Raises
    - `HTTPException(status_code=404)`: Raised when the user is not found.

    ### Example
    - Get profile: [GET] `/api/v1/contacts/{username}`"""
    user = await repository_profile.get_profile(username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    return user
