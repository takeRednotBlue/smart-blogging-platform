from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession
import src.repository.comments as repository_comments
from src.database.db import get_async_db
from src.database.models.comments import Comment
from src.database.models.user import User
from src.schemas.comments import CommentBase, CommentResponse
router = APIRouter(prefix='/posts', tags=['posts'])
current_user = User(id=1, username='Ivan')


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_post(db: AsyncSession=Depends(get_async_db)):
    """# create_post

### Description
This endpoint is used to create a new post.

### Authorization
- Access to this endpoint requires users to be authenticated.
- Allowed roles: "Admin", "Moderator", "User".
- The access JWT token should be passed in the request header for authentication.

### Request limit
- The allowed amount of requests per defined time is 3 requests per 60 seconds.

### Query Parameters
- None.

### Returns
- `Post`: The newly created post.

### Raises
- `HTTP_401_UNAUTHORIZED`: If the user is not authenticated.
- `HTTP_403_FORBIDDEN`: If the user does not have the required role to access this endpoint.

### Example
- Create a new post: [POST] `/api/v1/contacts/`"""
    post = await repository_comments.create_post(db)
    return post


@router.post('/user', status_code=status.HTTP_201_CREATED)
async def create_user(db: AsyncSession=Depends(get_async_db)):
    """# Create User

### Description
This endpoint is used to create a new user.

### Authorization
- Access to this endpoint requires users to be authenticated.
- Allowed roles: "Admin", "Moderator", "User".
- The access JWT token should be passed in the request header for authentication.

### Request limit
- Maximum 10 requests per 60 seconds.

### Query Parameters
None

### Returns
- `User`: The newly created user object.

### Raises
- `HTTP_201_CREATED`: The user was successfully created.

### Example
- Create a new user: [POST] `/api/v1/user`"""
    user = await repository_comments.create_user(db)
    return user


@router.post('/{post_id}/comments', dependencies=[Depends(RateLimiter(times
    =3, seconds=60))], response_model=CommentResponse, status_code=status.
    HTTP_201_CREATED)
async def create_comment(post_id: int, body: CommentBase, db: AsyncSession=
    Depends(get_async_db)) ->Comment:
    """# Create Comment

### Description
This endpoint allows authenticated users to create a comment for a specific post.

### Authorization
- Access to this endpoint requires users to be authenticated.
- Allowed roles: "Admin", "Moderator", "User".
- The access JWT token should be passed in the request header for authentication.

### Request limit
- Maximum of 3 requests per 60 seconds.

### Query Parameters
- `post_id` (**int**, required): The ID of the post to create the comment for.
- `body` (**CommentBase**, required): The body of the comment.

### Returns
- `CommentResponse`: The created comment.

### Raises
- `HTTPException(404)`: If the post is not found.

### Example
- Create a comment: [POST] `/api/v1/contacts/{post_id}/comments`"""
    comment = await repository_comments.create_comment(body, post_id,
        current_user, db)
    if comment:
        return comment
    raise HTTPException(404, detail='Post not found')


@router.get('/{post_id}/comments', response_model=list[CommentResponse])
async def read_post_comments(post_id: int, db: AsyncSession=Depends(
    get_async_db)):
    """# Read Post Comments

### Description
This endpoint retrieves the comments for a specific post.

### Authorization
- Access to this endpoint requires users to be authenticated.
- Allowed roles: "Admin", "Moderator", "User".
- The access JWT token should be passed in the request header for authentication.

### Request limit
- Maximum of 10 requests per 60 seconds.

### Query Parameters
- `post_id` (**int**, required): The ID of the post to retrieve comments for.

### Returns
- `list[CommentResponse]`: A list of comments for the specified post.

### Raises
- `HTTPException(404)`: If the comments for the post do not exist.

### Example
- Retrieve comments for post with ID 123: [GET] `/api/v1/contacts/123/comments`"""
    comments = await repository_comments.read_post_comment(post_id, db)
    if comments:
        return comments
    raise HTTPException(404, detail='Comments not exist')


@router.put('/{post_id}/comments/{comment_id}', description=
    'No more than 10 requests per minute', dependencies=[Depends(
    RateLimiter(times=10, seconds=60))], response_model=CommentResponse)
async def update_comment(post_id: int, comment_id: int, body: CommentBase,
    db: AsyncSession=Depends(get_async_db)) ->Comment:
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
- `post_id` (**int**, required): The ID of the post.
- `comment_id` (**int**, required): The ID of the comment.
- `body` (**CommentBase**, required): The updated comment data.

### Returns
- `CommentResponse`: The updated comment.

### Raises
- `HTTPException(404)`: If the post is not found.

### Example
- Update comment: [PUT] `/api/v1/comments/123/456`"""
    comment = await repository_comments.update_comment(body, post_id,
        comment_id, current_user, db)
    if not comment:
        raise HTTPException(404, detail='Post not found')
    return comment


@router.delete('/{post_id}/comments/{comment_id}', response_model=
    CommentResponse)
async def remove_comment(comment_id: int, db: AsyncSession=Depends(
    get_async_db)) ->Comment:
    """# Remove Comment

### Description
This endpoint is used to remove a comment from a post.

### Authorization
- Access to this endpoint requires users to be authenticated.
- Allowed roles: "Admin", "Moderator", "User".
- The access JWT token should be passed in the request header for authentication.

### Request limit
- Maximum of 10 requests per 60 seconds.

### Query Parameters
- `comment_id` (**int**, required): The ID of the comment to be removed.

### Returns
- `CommentResponse`: The response model containing the details of the deleted comment.

### Raises
- `HTTPException 404`: Raised if the comment is not found.

### Example
- Remove a comment: [DELETE] `/api/v1/contacts/{post_id}/comments/{comment_id}`"""
    deleted_comment = await repository_comments.remove_comment(comment_id, db)
    if deleted_comment:
        return JSONResponse(content={'message':
            'Comment successfully deleted', 'deleted_comment_id':
            deleted_comment.id, 'deleted_comment': deleted_comment.comment},
            status_code=200)
    raise HTTPException(404, detail='Comment not found')
