from typing import List, Annotated
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_async_db
from src.database.models.users import User
from src.services.auth import auth_service
from src.repository import ratings as repository_ratings
from src.schemas.ratings import RatingModel, RatingResponse, PostRatingResponse, UserRatingResponse
router = APIRouter(prefix='', tags=['ratings'])
async_db = Annotated[AsyncSession, Depends(get_async_db)]


@router.get('/post/{post_id}/rating', dependencies=[Depends(RateLimiter(
    times=5, seconds=60))])
async def read_rating_of_post(db: async_db, post_id, current_user: User=
    Depends(auth_service.get_current_user)) -> int:
    """# Read Rating of Post

    ### Description
    This endpoint retrieves the rating of a specific post.

    ### Authorization
    - Access to this endpoint requires users to be authenticated.
    - Allowed roles: "Admin", "Moderator", "User".
    - The access JWT token should be passed in the request header for authentication.

    ### Request limit
    - Maximum of 5 requests per 60 seconds.

    ### Query Parameters
    - `post_id` (**int**, required): The ID of the post.

    ### Returns
    - `int`: The rating of the post.

    ### Raises
    - `HTTPException(status_code=404)`: If the post is not found.

    ### Example
    - Retrieve rating of a post: [GET] `/post/{post_id}/rating`"""
    post = await repository_ratings.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=
            'Post not found.')
    return await repository_ratings.get_rating_of_post(db, post_id)


@router.get('/post/{post_id}/ratings', response_model=List[
    PostRatingResponse], dependencies=[Depends(RateLimiter(times=5, seconds
    =60))])
async def read_ratings_of_post(db: async_db, post_id, current_user: User=
    Depends(auth_service.get_current_user)) -> List[PostRatingResponse]:
    """# Read Ratings of Post

    ### Description
    This endpoint retrieves the ratings of a specific post.

    ### Authorization
    - Access to this endpoint requires users to be authenticated.
    - Allowed roles: "Admin", "Moderator", "User".
    - The access JWT token should be passed in the request header for authentication.

    ### Request limit
    - Maximum of 5 requests per 60 seconds.

    ### Query Parameters
    - `post_id` (**str**, required): The ID of the post.

    ### Returns
    - `List[PostRatingResponse]`: A list of post ratings.

    ### Raises
    - `HTTPException(status_code=status.HTTP_404_NOT_FOUND)`: If the post is not found.

    ### Example
    - Retrieve ratings of a post: [GET] `/post/{post_id}/ratings`"""
    post = await repository_ratings.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=
            'Post not found.')
    return await repository_ratings.get_ratings_of_post(db, post_id)


@router.get('/user/{user_id}/ratings', response_model=List[
    UserRatingResponse], dependencies=[Depends(RateLimiter(times=5, seconds
    =60))])
async def read_ratings_of_user(db: async_db, user_id, current_user: User=
    Depends(auth_service.get_current_user)) -> List[UserRatingResponse]:
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=
            'User not found.')
    return await repository_ratings.get_ratings_of_user(db, user_id)


@router.post('/post/{post_id}/ratings', response_model=RatingResponse,
    status_code=status.HTTP_201_CREATED, dependencies=[Depends(RateLimiter(
    times=5, seconds=60))])
async def add_rating_for_post(body: RatingModel, db: async_db, post_id: int,
    current_user: User=Depends(auth_service.get_current_user)
    ) -> RatingResponse:
    """# add_rating_for_post

    ### Description
    This endpoint allows authenticated users to add a rating for a specific post.

    ### Authorization
    - Access to this endpoint requires users to be authenticated.
    - Allowed roles: "Admin", "Moderator", "User".
    - The access JWT token should be passed in the request header for authentication.

    ### Request limit
    - The request limit for this endpoint is 5 requests per 60 seconds.

    ### Query Parameters
    - `post_id` (**int**, required): The ID of the post to add the rating for.

    ### Returns
    - `RatingResponse`: The response containing the added rating information.

    ### Raises
    - `HTTPException(status_code=status.HTTP_404_NOT_FOUND)`: If the post or user is not found.
    - `HTTPException(status_code=status.HTTP_400_BAD_REQUEST)`: If the user is the author of the post, or if the user has already rated the post.

    ### Example
    - Add rating for post: [POST] `/post/{post_id}/ratings`"""
    post = await repository_ratings.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=
            'Post not found.')
    user = await repository_ratings.get_user_by_id(db, body.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=
            'User not found.')
    is_user_author_of_post = await repository_ratings.is_user_author_of_post(db
        , body.user_id, post_id)
    if is_user_author_of_post:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail
            ="User can't estimate his own post.")
    user_estimated_post = await repository_ratings.user_estimated_post(db,
        body.user_id, post_id)
    if user_estimated_post:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail
            ='User has already estimated this post.')
    rating = await repository_ratings.add_rating_for_post(db, body, post_id)
    return rating


@router.delete('/post/{post_id}/ratings/{rating_id}', response_model=
    RatingResponse, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def delete_rating(db: async_db, post_id: int, rating_id: int,
    current_user: User=Depends(auth_service.get_current_user)
    ) -> RatingResponse:
    """# Delete Rating

    ### Description
    This endpoint allows authenticated users to delete a rating for a specific post.

    ### Authorization
    - Authentication is required.
    - Allowed roles: "Admin", "Moderator", "User".
    - Access JWT token should be passed in the request header for authentication.

    ### Request limit
    - Maximum of 5 requests per 60 seconds.

    ### Query Parameters
    - `post_id` (**int**, required): The ID of the post.
    - `rating_id` (**int**, required): The ID of the rating.

    ### Returns
    - `RatingResponse`: The response containing the details of the deleted rating.

    ### Raises
    - `HTTPException(status_code=404)`: If the post or rating is not found.

    ### Example
    - Delete rating: [DELETE] `/post/{post_id}/ratings/{rating_id}`"""
    post = await repository_ratings.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=
            'Post not found.')
    rating = await repository_ratings.rating_exists_for_post(db, post_id,
        rating_id)
    if not rating:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=
            'Rating not found.')
    return await repository_ratings.remove_rating_for_post(db, post_id,
        rating_id)
