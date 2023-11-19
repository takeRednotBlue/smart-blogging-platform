from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.posts import PostModel, PostResponse, PostResponseOne, PostUpdate
from src.repository import posts as repository_posts
from src.database.models.users import User
from src.database.db import get_async_db
from src.services.auth import auth_service
from fastapi_limiter import FastAPILimiter


router = APIRouter(prefix="/posts", tags=["posts"])


@router.get(
    "/",
    response_model=List[PostResponse],
    dependencies=[Depends(FastAPILimiter(times=10, seconds=60))],
)
async def get_all_posts(db: AsyncSession = Depends(get_async_db)):
    """# Get All Posts

    ### Description
    This endpoint retrieves all posts from the database.

    ### Authorization
    - Access to this endpoint requires users to be authenticated.
    - Allowed roles: "Admin", "Moderator", "User".
    - The access JWT token should be passed in the request header for authentication.

    ### Request limit
    - Maximum of 10 requests per 60 seconds.

    ### Query Parameters
    - None.

    ### Returns
    - List[PostResponse]: A list of post objects.

    ### Raises
    - None.

    ### Example
    - Get all posts: [GET] `/api/v1/posts/`"""
    posts = await repository_posts.get_posts(db)
    return posts


@router.get(
    "/{post_id}",
    response_model=PostResponseOne,
    dependencies=[Depends(FastAPILimiter(times=10, seconds=60))],
)
async def get_post(post_id: int, db: AsyncSession = Depends(get_async_db)):
    """# Get Post

    ### Description
    This endpoint retrieves a specific post by its ID.

    ### Authorization
    - Access to this endpoint requires users to be authenticated.
    - Allowed roles: "Admin", "Moderator", "User".
    - The access JWT token should be passed in the request header for authentication.

    ### Request limit
    - Maximum of 10 requests per 60 seconds.

    ### Query Parameters
    - `post_id` (**int**, required): The ID of the post to retrieve.

    ### Returns
    - `PostResponseOne`: The retrieved post.

    ### Raises
    - `HTTPException(status_code=404)`: If the post is not found.

    ### Example
    - Retrieve a post: [GET] `/api/v1/posts/1`"""
    post = await repository_posts.get_post(post_id, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.post(
    "/",
    response_model=PostResponse,
    tags=["posts"],
    dependencies=[Depends(FastAPILimiter(times=10, seconds=60))],
)
async def create_post(
    body: PostModel,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """# Create Post

    ### Description
    This endpoint allows authenticated users to create a new post.

    ### Authorization
    - Access to this endpoint requires users to be authenticated.
    - Allowed roles: "Admin", "Moderator", "User".
    - The access JWT token should be passed in the request header for authentication.

    ### Request limit
    - Maximum 10 requests per 60 seconds.

    ### Query Parameters
    - `body` (**PostModel**, required): The body of the post.

    ### Returns
    - `PostResponse`: The created post.

    ### Raises
    - `HTTPException 401`: Unauthorized - When the user is not authenticated.
    - `HTTPException 403`: Forbidden - When the user does not have the required role.

    ### Example
    - Create a post: [POST] `/api/v1/posts/`"""
    post = await repository_posts.create_post(body, current_user, db)
    return post


@router.put(
    "/{post_id}",
    response_model=PostResponse,
    dependencies=[Depends(FastAPILimiter(times=10, seconds=60))],
)
async def update_post(
    body: PostUpdate,
    post_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """# Update Post

    ### Description
    This endpoint is used to update a post with the given post ID.

    ### Authorization
    - Access to this endpoint requires users to be authenticated.
    - Allowed roles: "Admin", "Moderator", "User".
    - The access JWT token should be passed in the request header for authentication.

    ### Request limit
    - Maximum 10 requests per 60 seconds.

    ### Query Parameters
    - `post_id` (**int**, required): The ID of the post to be updated.
    - `body` (**PostUpdate**, required): The updated post data.

    ### Returns
    - `PostResponse`: The updated post data.

    ### Raises
    - `HTTPException(status_code=404)`: If the post with the given ID is not found.

    ### Example
    - Update a post: [PUT] `/api/v1/posts/{post_id}`"""
    post = await repository_posts.update_post(post_id, current_user, body, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.delete(
    "/{post_id}",
    response_model=PostResponse,
    dependencies=[Depends(FastAPILimiter(times=10, seconds=60))],
)
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """# Delete Post

    ### Description
    This endpoint allows authenticated users to delete a post by its ID.

    ### Authorization
    - Access to this endpoint requires users to be authenticated.
    - Allowed roles: "Admin", "Moderator", "User".
    - The access JWT token should be passed in the request header for authentication.

    ### Request limit
    - Maximum 10 requests per 60 seconds.

    ### Query Parameters
    - `post_id` (**int**, required): The ID of the post to be deleted.

    ### Returns
    - `PostResponse`: The deleted post.

    ### Raises
    - `HTTPException(status_code=404)`: If the post is not found.

    ### Example
    - Delete post: [DELETE] `/api/v1/posts/{post_id}`"""
    post = await repository_posts.remove_post(post_id, current_user, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post
