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
    "/",
    response_model=List[TagResponse],
    dependencies=[RequestLimiter],
)
async def read_tags(
    db: AsyncDBSession,
) -> List[TagResponse]:
    """
    ### Description
    Returns a list of tag responses.

    ### Authorization
    - Only authorized user can get all tags.


    ### Query Parameters
    - `db` (**AsyncDBSession**): The async database connection.
    - `current_user` (**User**): The current authenticated user.

    ### Returns
    - `List[TagResponse]`: A list of tag responses.
    """
    return await repository_tags.get_tags(db)


@router.post(
    "/",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequestLimiter, AuthRequired],
)
async def create_tag(
    body: TagModel,
    db: AsyncDBSession,
) -> Tag:
    """
    ### Description
    Creates a new tag.

    ### Authorization
    - Only authorized user can create new tag.

    ### Query Parameters
    - `body` (**TagModel**): The tag model containing the tag information.
    - `db` (**AsyncDBSession**): The async database connection.
    - `current_user` (**User**): The current authenticated user.

    ### Returns
    - `TagModel`: The created tag.

    ### Raises
    - `Exeption with 409 HTTP code`: If the tag already exists.
    """
    tag = await repository_tags.get_tag(body.name, db)
    if tag:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Tag already exists"
        )
    return await repository_tags.create_tag(body, db)


@router.get(
    "/{tagname}",
    response_model=TagResponse,
    dependencies=[RequestLimiter],
)
async def read_tag(
    db: AsyncDBSession,
    tagname: str = Path(description="The name of the tag to get"),
) -> Tag:
    """
    ### Description
    This function is a GET endpoint that retrieves a tag by its name.

    ### Authorization
    - Only authorized user can get the tag.

    ### Query Parameters
    - `db` (**AsyncDBSession**): The async database connection.
    - `tagname` (**str**): The name of the tag to get.
    - `current_user` (**User**): The current authenticated user.

    ### Returns
    - `TagResponse`: It returns a `TagResponse` object.

    ### Raises
    - `Exeption with 404 HTTP code`: If the tag is not found.

    """
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
    """
    ### Description
    Updates a tag with the given name.

    ### Authorization
    - Only authorized user can change the tag.

    ### Query Parameters

    - `tagname` (**str**): The name of the tag to update.
    - `body` (**TagModel**): The updated tag model.
    - `db` (**AsyncDBSession**): The async database connection.
    - `current_user` (**User**): The current authenticated user.

    ### Returns
    - `Tag`: The updated tag.

    ### Raises
    - `Exeption with 404 HTTP code`: If the tag is not found.
    """
    tag = await repository_tags.update_tag(tagname, body, db)
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )
    return tag


@router.delete(
    "/{tagname}",
    response_model=TagResponse,
    dependencies=[
        RequestLimiter,
        AuthRequired,
        Depends(allowed_delete_tags),
    ],
)
async def remove_tag(
    db: AsyncDBSession,
    tagname: str = Path(description="The name of the tag to delete"),
) -> Tag:
    """
    ### Description
    Deletes a tag from the database.

    ### Authorization
    - Only authorized user can remove the tag.

    ### Query Parameters

    - `tagname` (**str**): The name of the tag to update.
    - `db` (**AsyncDBSession**): The async database connection.
    - `current_user` (**User**): The current authenticated user.

    ### Returns
    - `Tag`: The deleted tag.

    ### Raises
    - `Exeption with 404 HTTP code`: If the tag is not found.
    - `Exeption with 422 HTTP code`: If there is an error deleting the tag.

    """
    tag = await repository_tags.remove_tag(tagname, db)
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )
    return tag
