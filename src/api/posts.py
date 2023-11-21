from fastapi.responses import JSONResponse
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

import src.repository.comments as repository_comments
from src.database.db import get_async_db
from src.database.models.comments import Comment
from src.database.models.users import User
from src.repository import posts as repository_posts
from src.schemas.comments import CommentBase, CommentResponse
from src.schemas.posts import (
    PostModel,
    PostResponse,
    PostResponseOne,
    PostUpdate,
)
from src.services.auth import auth_service

router = APIRouter(prefix="/posts", tags=["posts"])
RequestLimiter = Depends(RateLimiter(times=10, seconds=60))
AsyncDBSession = Annotated[AsyncSession, Depends(get_async_db)]
AuthCurrentUser = Annotated[User, Depends(auth_service.get_current_user)]


@router.get(
    "/",
    response_model=List[PostResponse],
    dependencies=[RequestLimiter],
)
async def get_all_posts(db: AsyncDBSession):
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
    dependencies=[RequestLimiter],
)
async def get_post(post_id: int, db: AsyncDBSession):
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
    dependencies=[RequestLimiter],
    status_code=status.HTTP_201_CREATED,
)
async def create_post(
    body: PostModel,
    db: AsyncDBSession,
    current_user: AuthCurrentUser,
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
    dependencies=[RequestLimiter],
)
async def update_post(
    body: PostUpdate,
    post_id: int,
    db: AsyncDBSession,
    current_user: AuthCurrentUser,
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
    dependencies=[RequestLimiter],
)
async def delete_post(
    post_id: int,
    db: AsyncDBSession,
    current_user: AuthCurrentUser,
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


@router.post(
    "/{post_id}/comments",
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    post_id: int,
    body: CommentBase,
    db: AsyncDBSession,
    current_user: AuthCurrentUser,
) -> Comment:
    """# Create Comment

    ### Description
    This endpoint allows authenticated users to create a comment for a specific post.

    ### Authorization
    - Access to this endpoint requires users to be authenticated.
    - Allowed roles: "Admin", "Moderator", "User".
    - The access JWT token should be passed in the request header for authentication.

    ### Request limit
    - Maximum of 5 requests per 60 seconds.

    ### Query Parameters
    - `post_id` (**int**, required): The ID of the post to create the comment for.
    - `body` (**CommentBase**, required): The body of the comment.

    ### Returns
    - `CommentResponse`: The created comment.

    ### Raises
    - `HTTPException(404)`: If the post is not found.

    ### Example
    - Create a comment: [POST] `/api/v1/contacts/{post_id}/comments`"""
    comment = await repository_comments.create_comment(body, post_id, current_user, db)
    if comment:
        return comment
    raise HTTPException(404, detail="Post not found")


@router.get("/{post_id}/comments", response_model=list[CommentResponse])
async def read_post_comments(post_id: int, db: AsyncDBSession):
    """# Read Post Comments

    ### Description
    This endpoint retrieves the comments for a specific post.

    ### Authorization
    - Access to this endpoint requires users to be authenticated.
    - Allowed roles: "Admin", "Moderator", "User".
    - The access JWT token should be passed in the request header for authentication.

    ### Request limit
    - No limit

    ### Query Parameters
    - `post_id` (**int**, required): The ID of the post to retrieve comments for.

    ### Returns
    - `list[CommentResponse]`: A list of comments for the specified post.

    ### Raises
    - `HTTPException(404)`: If the comments for the post do not exist.

    ### Example
    - Retrieve comments for post with ID 123: [GET] `/api/v1/posts/123/comments`
    """
    comments = await repository_comments.read_post_comment(post_id, db)
    if comments:
        return comments
    raise HTTPException(404, detail="Comments not found")


@router.put(
    "/{post_id}/comments/{comment_id}",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
    response_model=CommentResponse,
)
async def update_comment(
    comment_id: int,
    body: CommentBase,
    current_user: AuthCurrentUser,
    db: AsyncDBSession,
) -> Comment:
    """# Update Comment

    ### Description
    This endpoint allows users to update a comment on a post.

    ### Authorization
    - Access to this endpoint requires users to be authenticated.
    - Allowed roles: "Admin", "Moderator", "User".
    - The access JWT token should be passed in the request header for authentication.

    ### Request limit
    - No more than 10 requests per minute.

    ### Query Parameters
    - `comment_id` (**int**, required): The ID of the comment.
    - `body` (**CommentBase**, required): The updated comment data.

    ### Returns
    - `CommentResponse`: The updated comment.

    ### Raises
    - `HTTPException(404)`: If the post is not found.

    ### Example
    - Update comment: [PUT] `/api/v1/posts/{post_id}/comments/{comment_id}`"""
    comment = await repository_comments.update_comment(body, comment_id, current_user, db)
    if not comment:
        raise HTTPException(404, detail="Post not found")
    return comment


@router.delete("/{post_id}/comments/{comment_id}", response_model=CommentResponse)
async def remove_comment(comment_id: int, db: AsyncDBSession) -> Comment:
    """# Remove Comment

    ### Description
    This endpoint is used to remove a comment from a post.

    ### Authorization
    - Access to this endpoint requires users to be authenticated.
    - Allowed roles: "Admin", "Moderator", "User".
    - The access JWT token should be passed in the request header for authentication.

    ### Request limit
    - No limit

    ### Query Parameters
    - `comment_id` (**int**, required): The ID of the comment to be removed.

    ### Returns
    - `CommentResponse`: The response model containing the details of the deleted comment.

    ### Raises
    - `HTTPException 404`: Raised if the comment is not found.

    ### Example
    - Remove a comment: [DELETE] `/api/v1/contacts/{post_id}/comments/{comment_id}`
    """
    deleted_comment = await repository_comments.remove_comment(comment_id, db)
    if deleted_comment:
        return JSONResponse(
            content={
                "message": "Comment successfully deleted",
                "deleted_comment_id": deleted_comment.id,
                "deleted_comment": deleted_comment.comment,
            },
            status_code=200,
        )
    raise HTTPException(404, detail="Comment not found")
