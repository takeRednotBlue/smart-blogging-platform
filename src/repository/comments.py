from typing import List

from fastapi import HTTPException
from sqlalchemy import func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.database.models.comments import Comment
from src.database.models.posts import Post  # noqa
from src.database.models.users import User
from src.schemas.comments import CommentBase


async def create_comment(
    body: CommentBase, post_id: int, user: User, db: AsyncSession
) -> Comment:
    """Creates a comment for a post.

    :param body: The body of the comment.
    :type body: CommentBase
    :param post_id: The ID of the post.
    :type post_id: int
    :param user: The user who is creating the comment.
    :type user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: The created comment.
    :rtype: Comment"""
    post = await db.execute(select(Post).where(Post.id == post_id))
    post = post.scalars().first()
    if post:
        comment = Comment(
            **body.model_dump(), user_id=user.id, post_id=post.id
        )
        db.add(comment)
        await db.commit()
        await db.refresh(comment)
        return comment
    return None


async def read_post_comment(post_id: int, db: AsyncSession) -> List[Comment]:
    """Retrieves the comments for a given post from the database.

    :param db: The database session.
    :type db: AsyncSession
    :return: A list of Comment objects associated with the post.
    :rtype: List[Comment]
    """
    comments = await db.execute(
        select(Comment).where(Comment.post_id == post_id)
    )
    return comments.scalars().all()


async def update_comment(
    body: CommentBase, comment_id: int, user: User, db: AsyncSession
) -> Comment:
    """Updates a comment in the database.

    :param body: The updated comment data.
    :type body: CommentBase
    :param post_id: The ID of the post that the comment belongs to.
    :type post_id: int
    :param comment_id: The ID of the comment to be updated.
    :type comment_id: int
    :param user: The user making the update request.
    :type user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: The updated comment.
    :rtype: Comment
    :raises HTTPException 404: If the comment is not found.
    :raises HTTPException 403: If the user does not have permission to update the comment.
    """
    comment = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = comment.scalars().first()
    if not comment:
        raise HTTPException(404, detail="Comment not found")
    if comment.user_id != user.id:
        raise HTTPException(
            403,
            detail="Permission denied: You can only update your own comments",
        )

    await db.execute(
        update(Comment)
        .where(Comment.id == comment_id)
        .values({"comment": body.comment, "updated_at": func.now()})
    )
    await db.commit()
    await db.refresh(comment)
    return comment


async def remove_comment(comment_id: int, db: AsyncSession) -> Comment:
    """Removes a comment from the database.

    :param comment_id: The ID of the comment to be removed.
    :type comment_id: int
    :param db: The database session.
    :type db: AsyncSession
    :return: The removed comment, or None if the comment does not exist.
    :rtype: Comment"""
    removed_comment = await db.execute(
        select(Comment)
        .where(Comment.id == comment_id)
        .options(selectinload(Comment.user))
    )
    removed_comment = removed_comment.scalar()
    if removed_comment:
        await db.delete(removed_comment)
        await db.commit()
    return removed_comment
