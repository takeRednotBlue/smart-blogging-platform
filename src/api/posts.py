import logging
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

import src.repository.comments as repository_comments
import src.repository.posts as repository_posts
from src.database.db import get_async_db
from src.database.models.comments import Comment
from src.database.models.users import Roles, User
from src.repository import ratings as repository_ratings
from src.schemas.comments import CommentBase, CommentResponse
from src.schemas.posts import (
    PostModel,
    PostResponse,
    PostResponseOne,
    PostUpdate,
)
from src.schemas.ratings import PostRatingResponse, RatingModel, RatingResponse
from src.services.auth import auth_service
from src.services.role_checker import RoleChecker

router = APIRouter(prefix="/posts", tags=["posts"])

# Dependencies
RequestLimiter = Depends(RateLimiter(times=10, seconds=60))
AsyncDBSession = Annotated[AsyncSession, Depends(get_async_db)]
AuthCurrentUser = Annotated[User, Depends(auth_service.get_current_user)]

# Allowed roles to access endpoint
allowed_delete_comment = RoleChecker([Roles.admin, Roles.moderator])

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return post


@router.post(
    "/",
    response_model=PostResponse,
    tags=["posts"],
    dependencies=[RequestLimiter],
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return post


@router.post(
    "/{post_id}/comments",
    dependencies=[RequestLimiter],
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["comments"],
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
    comment = await repository_comments.create_comment(
        body, post_id, current_user, db
    )
    if comment:
        return comment
    raise HTTPException(404, detail="Post not found")


@router.get(
    "/{post_id}/comments",
    response_model=list[CommentResponse],
    tags=["comments"],
)
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
    tags=["comments"],
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
    comment = await repository_comments.update_comment(
        body, comment_id, current_user, db
    )
    if not comment:
        raise HTTPException(404, detail="Post not found")
    return comment


@router.delete(
    "/{post_id}/comments/{comment_id}",
    response_model=CommentResponse,
    dependencies=[Depends(allowed_delete_comment)],
    tags=["comments"],
)
async def remove_comment(
    comment_id: int, db: AsyncDBSession, current_user: AuthCurrentUser
) -> Comment:
    """# Remove Comment

    ### Description
    This endpoint is used to remove a comment from a post.

    ### Authorization
    - Access to this endpoint requires users to be authenticated.
    - Allowed roles: "Admin", "Moderator".
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
        logger.info(
            f"Current user {current_user.email} with role '{current_user.roles.value}' \
deleted comment '{deleted_comment.comment}' on post with ID '{deleted_comment.post_id}' \
left by '{deleted_comment.user.username}'."
        )
        return JSONResponse(
            content={
                "message": "Comment successfully deleted",
                "deleted_comment_id": deleted_comment.id,
                "deleted_comment": deleted_comment.comment,
            },
            status_code=200,
        )
    raise HTTPException(404, detail="Comment not found")


@router.get(
    "/{post_id}/rating",
    dependencies=[RequestLimiter],
    tags=["ratings"],
)
async def read_rating_of_post(
    db: AsyncDBSession,
    post_id,
    current_user: User = Depends(auth_service.get_current_user),
) -> int:
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found."
        )
    return await repository_ratings.get_rating_of_post(db, post_id)


@router.get(
    "/{post_id}/ratings",
    response_model=List[PostRatingResponse],
    dependencies=[RequestLimiter],
    tags=["ratings"],
)
async def read_ratings_of_post(
    db: AsyncDBSession,
    post_id,
    current_user: User = Depends(auth_service.get_current_user),
) -> List[PostRatingResponse]:
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found."
        )
    return await repository_ratings.get_ratings_of_post(db, post_id)


@router.delete(
    "/{post_id}/ratings/{rating_id}",
    response_model=RatingResponse,
    dependencies=[RequestLimiter],
    tags=["ratings"],
)
async def delete_rating(
    db: AsyncDBSession,
    post_id: int,
    rating_id: int,
    current_user: User = Depends(auth_service.get_current_user),
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found."
        )
    rating = await repository_ratings.rating_exists_for_post(
        db, post_id, rating_id
    )
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found."
        )
    return await repository_ratings.remove_rating_for_post(
        db, post_id, rating_id
    )


@router.post(
    "/{post_id}/ratings",
    response_model=RatingResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequestLimiter],
    tags=["ratings"],
)
async def add_rating_for_post(
    body: RatingModel,
    db: AsyncDBSession,
    post_id: int,
    current_user: User = Depends(auth_service.get_current_user),
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found."
        )
    user = await repository_ratings.get_user_by_id(db, body.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    is_user_author_of_post = await repository_ratings.is_user_author_of_post(
        db, body.user_id, post_id
    )
    if is_user_author_of_post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User can't estimate his own post.",
        )
    user_estimated_post = await repository_ratings.user_estimated_post(
        db, body.user_id, post_id
    )
    if user_estimated_post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has already estimated this post.",
        )
    rating = await repository_ratings.add_rating_for_post(db, body, post_id)
    return rating
