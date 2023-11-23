from typing import Annotated
import uuid
from easy_open_ai import aget_picture_url

from fastapi import APIRouter, Depends, Query
from fastapi_limiter.depends import RateLimiter

from src.database.models.users import User
from src.services.auth import auth_service
from src.services.cloudinarry import upload_image_to_cloudinary

# Dependencies
AuthCurrentUser = Annotated[User, Depends(auth_service.get_current_user)]
RequestLimiter = Depends(RateLimiter(times=60, seconds=60))

generate_picture_router = APIRouter(
    prefix="/illustrate",
    tags=["pictures"],
)


@generate_picture_router(
    "/",
    name="get_illustration",
    dependencies=[RequestLimiter, AuthCurrentUser], # actually later we'll to pass user id as an input to the function I think
)
async def illustrate(
    current_user: AuthCurrentUser,
    query_param: str = Query(..., description="A prompt for DALLE"),
):
    """# Illustrate Text

    ### Description
    This endpoint provides OpenAI illustration suggestions for a given text. Meant to be used for posts banner, attached picture or anything you like.

    ### Authorization
    - Access to this endpoint requires users to be authenticated.
    - Allowed roles: "Admin", "Moderator", "User".
    - The access JWT token should be passed in the request header for authentication.

    ### Request limit
    - Maximum 60 requests per 60 seconds.

    ### Query Parameters
    - `query_param` (**str**, required): Illustration query.

    ### Returns
    - `dict`: A dictionary containing the illustration and its uuid, so it can be easily found and removed when necessary.

    ### Raises
    - `HTTPException 422`: If the query parameter is missing or invalid.
    - `HTTPException 429`: If too many requests.

    ### Example
    - Get autocomplete suggestion: [GET] `/api/v1/illustrate/?query_param=cat`
    """
    temporary_url = await aget_picture_url(query_param)  # this url lives for 1 hour
    image_name = str(uuid.uuid4())
    illustration = await upload_image_to_cloudinary(
        current_user.id, temporary_url, image_name, unique=False # it's definitely unique
    )
    return {"illustration_id": image_name, "illustration": illustration}

# need to implement cloudinary removal