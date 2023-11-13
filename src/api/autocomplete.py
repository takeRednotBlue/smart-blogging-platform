from fastapi import APIRouter, Query, Request
from fastapi_limiter.depends import RateLimiter
from src.services.autocomplete import exmple_list_autocoplete
from easy_open_ai import aautocomplete_text


autocomplete_router = APIRouter(prefix="/autocomplete")

times = 90

autocomplete_rate_limiters = {
    "text_autocomplete": RateLimiter(times=times, seconds=60),
    "fruits_list_autocomplete": RateLimiter(times=times, seconds=60),
}


async def autocomplete_rate_limiter_middleware(request: Request, call_next):
    """LIMITER MIDDLEWARE"""
    path = request.url.path
    rate_limiter = autocomplete_rate_limiters.get(path)

    if rate_limiter:
        await rate_limiter(request)

    response = await call_next(request)
    return response


@autocomplete_router.get("/", name="text_autocomplete")
async def autocomplete_text(
    query_param: str = Query(..., description="Autocomplete query")
):
    """# Autocomplete Text

    ### Description
    This endpoint provides OpenAI autocomplete suggestions for a given query.

    ### Authorization
    - Access to this endpoint requires users to be authenticated.
    - Allowed roles: "Admin", "Moderator", "User".
    - The access JWT token should be passed in the request header for authentication.

    ### Request limit
    - Maximum 90 requests per 60 seconds.

    ### Query Parameters
    - `query_param` (**str**, required): Autocomplete query.

    ### Returns
    - `dict`: A dictionary containing the autocomplete suggestion.

    ### Raises
    - `HTTPException 422`: If the query parameter is missing or invalid.

    ### Example
    - Get autocomplete suggestion: [GET] `/api/v1/autocomplete/?query_param=example`"""
    suggestion = await aautocomplete_text(query_param)
    return {"suggestion": suggestion}


@autocomplete_router.get("/fruits", name="fruits_list_autocomplete")
async def autocomplete_fruits(
    query_param: str = Query(..., description="Autocomplete query")
):
    """# Autocomplete Fruits

    ### Description
    This endpoint provides a list of autocomplete suggestions for a given query parameter.

    ### Authorization
    - Access to this endpoint requires users to be authenticated.
    - Allowed roles: "Admin", "Moderator", "User".
    - The access JWT token should be passed in the request header for authentication.

    ### Request limit
    - Maximum 90 requests per 60 seconds.

    ### Query Parameters
    - `query_param` (**str**, required): Autocomplete query.

    ### Returns
    - `dict`: A dictionary containing the autocomplete suggestions.

    ### Raises
    - `HTTPException 422`: If the query parameter is missing or invalid.

    ### Example
    - Autocomplete Text: [GET] `/fruits?query_param=appl`"""
    suggestions = exmple_list_autocoplete(query_param)
    return {"suggestions": suggestions}
