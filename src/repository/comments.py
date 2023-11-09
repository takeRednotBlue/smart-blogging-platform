from datetime import datetime, timedelta
from typing import List

from sqlalchemy import and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models.comments import Comment 
from src.database.models.user import User
from src.schemas.comments import CommentBase


async def create_comment(body: CommentBase, user: User, db: AsyncSession) -> Comment:
    comment = Comment(**body.model_dump(), user_id=user.id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

