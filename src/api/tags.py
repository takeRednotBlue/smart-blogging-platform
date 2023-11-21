from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_async_db
from src.database.models.tags import Tag
from src.database.models.users import Roles, User
from src.repository import tags as repository_tags
from src.schemas.tags import TagModel, TagResponse
from src.services.auth import auth_service
from src.services.role_checker import RoleChecker

# Dependencies
RequestLimiter = Depends(RateLimiter(times=10, seconds=60))
AsyncDBSession = Annotated[AsyncSession, Depends(get_async_db)]
AuthCurrentUser = Annotated[User, Depends(auth_service.get_current_user)]
AuthRequired = Depends(auth_service.get_current_user)

# Allowed roles
allowed_delete_tags = RoleChecker([Roles.admin, Roles.moderator])
allowed_update_tags = RoleChecker([Roles.admin, Roles.moderator])

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get(
    "/", response_model=List[TagResponse], dependencies=[RequestLimiter]
)
async def read_tags(db: AsyncDBSession) -> List[TagResponse]:
    """# Read Tags

    ### Description
    This endpoint retrieves a list of tags from the database.

    ### Authorization
    - Allowed roles: "Admin", "Moderator", "User".

    ### Request limit
    - Maximum of 10 requests per 60 seconds.

    ### Query Parameters
    - None.

    ### Returns
    - List[TagResponse]: A list of tags retrieved from the database.

    ### Raises
    - None.

    ### Example
    - GET `http://example.com/api/v1/contacts/`"""
    return await repository_tags.get_tags(db)


@router.post(
    "/",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequestLimiter, AuthRequired],
)
async def create_tag(body: TagModel, db: AsyncDBSession) -> Tag:
    """# Create Tag

    ### Description
    This endpoint is used to create a new tag.

    ### Authorization
    - Access to this endpoint requires users to be authenticated.
    - Allowed roles: "Admin", "Moderator", "User".
    - The access JWT token should be passed in the request header for authentication.

    ### Request limit
    - Maximum 10 requests per 60 seconds.

    ### Query Parameters
    - `body` (**TagModel**, required): The tag data to be created.

    ### Returns
    - `TagResponse`: The created tag data.

    ### Raises
    - `HTTPException(status_code=409)`: If the tag already exists.

    ### Example
    - Create a new tag: [POST] `/api/v1/contacts/`"""
    tag = await repository_tags.get_tag(body.name, db)
    if tag:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Tag already exists"
        )
    return await repository_tags.create_tag(body, db)


@router.get(
    "/{tagname}", response_model=TagResponse, dependencies=[RequestLimiter]
)
async def read_tag(
    db: AsyncDBSession,
    tagname: str = Path(description="The name of the tag to get"),
) -> Tag:
    """# Get Tag

    ### Description
    This endpoint retrieves a tag by its name.

    ### Authorization
    - Allowed roles: "Admin", "Moderator", "User".

    ### Request limit
    - Maximum of 10 requests per 60 seconds.

    ### Query Parameters
    - `tagname` (**str**, optional): The name of the tag to get.

    ### Returns
    - `TagResponse`: The retrieved tag.

    ### Raises
    - `HTTPException(status_code=404)`: If the tag is not found.

    ### Example
    - Get tag: [GET] `/api/v1/contacts/{tagname}`"""
    tag = await repository_tags.get_tag(tagname, db)
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )
    return tag


@router.put(
    "/{tagname}",
    response_model=TagResponse,
    dependencies=[RequestLimiter, AuthRequired, Depends(allowed_update_tags)],
)
async def update_tag(
    body: TagModel,
    db: AsyncDBSession,
    tagname: str = Path(description="The name of the tag to put"),
) -> Tag:
    """# Update Tag

    ### Description
    This endpoint allows authenticated users with the roles "Admin", "Moderator", or "User" to update a tag. The tag is identified by its name.

    ### Authorization
    - Access to this endpoint requires authentication.
    - Allowed roles: "Admin", "Moderator".
    - The access JWT token should be passed in the request header for authentication.

    ### Request limit
    - Maximum of 10 requests per 60 seconds.

    ### Query Parameters
    - `tagname` (**str**, required): The name of the tag to update.

    ### Returns
    - `TagResponse`: The updated tag information.

    ### Raises
    - `HTTPException(status_code=404)`: If the tag is not found.

    ### Example
    - Update tag: [PUT] `/api/v1/contacts/{tagname}`"""
    tag = await repository_tags.update_tag(tagname, body, db)
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )
    return tag


@router.delete(
    "/{tagname}",
    response_model=TagResponse,
    dependencies=[RequestLimiter, AuthRequired, Depends(allowed_delete_tags)],
)
async def remove_tag(
    db: AsyncDBSession,
    tagname: str = Path(description="The name of the tag to delete"),
) -> Tag:
    """# Remove Tag

    ### Description
    This endpoint is used to remove a tag from the database.

    ### Authorization
    - Access to this endpoint requires users to be authenticated.
    - Allowed roles: "Admin", "Moderator".
    - The access JWT token should be passed in the request header for authentication.

    ### Request limit
    - Maximum of 10 requests per 60 seconds.

    ### Query Parameters
    - `tagname` (**str**, required): The name of the tag to delete.

    ### Returns
    - `TagResponse`: The response containing the details of the deleted tag.

    ### Raises
    - `HTTPException(status_code=404)`: If the tag is not found in the database.

    ### Example
    - Delete tag: DELETE `http://example.com/api/v1/contacts/{tagname}`"""
    tag = await repository_tags.remove_tag(tagname, db)
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )
    return tag
