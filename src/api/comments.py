
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

import src.repository.comments as repository_comments
from src.schemas.comments import CommentResponse, CommentBase
from src.database.models.user import User
from src.database.db import get_async_db



router = APIRouter(prefix="/comments", tags=["comments"])

current_user = User(id=1, username='Ivan')

@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: CommentBase,
    # current_user: User = current_user,
    db: AsyncSession = Depends(get_async_db),
):

    comment = await repository_comments.create_comment(body, current_user, db)
    return comment
