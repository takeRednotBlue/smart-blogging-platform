from typing import Union, List, Annotated

from fastapi import Path, APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_async_db
from src.repository import tags as repository_tags
from src.database.models.tags import Tag
from src.database.models.users import User
from src.schemas.tags import TagModel, TagResponse
from src.services.auth import auth_service


router = APIRouter(prefix="/tags", tags=["tags"])

RequestLimiter = Depends(RateLimiter(times=10, seconds=60))
AsyncDBSession = Annotated[AsyncSession, Depends(get_async_db)]
AuthCurrentUser = Annotated[User, Depends(auth_service.get_current_user)]


@router.get(
    "/",
    response_model=List[TagResponse],
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
async def read_tags(
    db: AsyncDBSession,
    current_user: User = Depends(auth_service.get_current_user),
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
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
async def create_tag(
    body: TagModel,
    db: AsyncDBSession,
    current_user: User = Depends(auth_service.get_current_user),
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
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
async def read_tag(
    db: AsyncDBSession,
    tagname: str = Path(description="The name of the tag to get"),
    current_user: User = Depends(auth_service.get_current_user),
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
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
async def update_tag(
    body: TagModel,
    db: AsyncDBSession,
    tagname: str = Path(description="The name of the tag to put"),
    current_user: User = Depends(auth_service.get_current_user),
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
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
async def remove_tag(
    db: AsyncDBSession,
    tagname: str = Path(description="The name of the tag to delete"),
    current_user: User = Depends(auth_service.get_current_user),
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
