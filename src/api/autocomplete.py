from typing import Annotated
from easy_open_ai import aautocomplete_text
from fastapi import APIRouter, Depends, Query
from fastapi_limiter.depends import RateLimiter

from src.services.auth import auth_service
from src.services.autocomplete import exmple_list_autocoplete, list_suggestions
from src.database.db import get_async_db
from src.repository.tags import get_tags

from sqlalchemy.ext.asyncio import AsyncSession

# Dependencies
AuthRequired = Depends(auth_service.get_current_user)
RequestLimiter = Depends(RateLimiter(times=60, seconds=60))
AsyncDBSession = Annotated[AsyncSession, Depends(get_async_db)]

autocomplete_router = APIRouter(
    prefix="/autocomplete",
    tags=["autocomplete"],
    dependencies=[AuthRequired],
)


@autocomplete_router.get(
    "/",
    name="text_autocomplete",
    dependencies=[RequestLimiter, AuthRequired],
)
async def autocomplete_text(
    query_param: str = Query(..., description="Autocomplete query"),
):
    """# Autocomplete Text

    ### Description
    This endpoint provides OpenAI autocomplete suggestions for a given query.

    ### Authorization
    - Access to this endpoint requires users to be authenticated.
    - Allowed roles: "Admin", "Moderator", "User".
    - The access JWT token should be passed in the request header for authentication.

    ### Request limit
    - Maximum 60 requests per 60 seconds.

    ### Query Parameters
    - `query_param` (**str**, required): Autocomplete query.

    ### Returns
    - `dict`: A dictionary containing the autocomplete suggestion.

    ### Raises
    - `HTTPException 422`: If the query parameter is missing or invalid.
    - `HTTPException 429`: If too many requests.

    ### Example
    - Get autocomplete suggestion: [GET] `/api/v1/autocomplete/?query_param=example`
    """
    suggestion = await aautocomplete_text(query_param)
    return {"suggestion": suggestion}

@autocomplete_router.get(
    "/tags",
    name="tags_list_autocomplete",
    dependencies=[RequestLimiter, AuthRequired],
)
async def autocomplete_tags(
    db: AsyncDBSession, query_param: str = Query(..., description="Autocomplete query")
):
    """# Autocomplete Tags

    ### Description
    This endpoint provides a list of autocomplete suggestions for a given query parameter.

    ### Authorization
    - Access to this endpoint requires users to be authenticated.
    - Allowed roles: "Admin", "Moderator", "User".
    - The access JWT token should be passed in the request header for authentication.

    ### Request limit
    - Maximum 60 requests per 60 seconds.

    ### Query Parameters
    - `query_param` (**str**, required): Autocomplete query.

    ### Returns
    - `dict`: A dictionary containing the autocomplete suggestions.

    ### Raises
    - `HTTPException 422`: If the query parameter is missing or invalid.
    - `HTTPException 429`: If too many requests.

    ### Example
    - Autocomplete Text: [GET] `/tags?query_param=tag`"""
    all_tag_objects = await get_tags(db)
    all_tags = [tag.name for tag in all_tag_objects]
    suggestions = list_suggestions(query_param, all_tags)
    return {"suggestions": suggestions}
