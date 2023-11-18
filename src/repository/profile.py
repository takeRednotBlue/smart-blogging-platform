from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.users import Post, User


async def get_profile(username: str, db: AsyncSession):
    """Retrieves the profile information of a user from the database.

    :param username: The username of the user.
    :type username: str
    :param db: The database session.
    :type db: AsyncSession
    :return: A dictionary containing the user's profile information, including username, email, creation date, description, and the number of posts made by the user. Returns None if the user does not exist.
    :rtype: dict or None"""
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    user = result.scalars().first()
    if user:
        query = select(Post).where(Post.user_id == user.id)
        result = await db.execute(query)
        number_of_posts = len(result.scalars().all())
        result = {
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at,
            "description": user.description,
            "number_of_posts": number_of_posts,
        }
        return result
    return None


async def get_profile_info(current_user: User, db: AsyncSession):
    """Retrieves the profile information of the current user.

    :param current_user: The current user object.
    :type current_user: User
    :param db: The asynchronous session object.
    :type db: AsyncSession
    :return: A dictionary containing the profile information of the user, including username, email, description, and roles. Returns None if the user does not exist.
    :rtype: dict or None"""
    query = select(User).where(User.id == current_user.id)
    result = await db.execute(query)
    user = result.scalars().first()
    if user:
        result = {
            "username": user.username,
            "email": user.email,
            "description": user.description,
            "roles": user.roles,
        }
        return result
    return None


async def update_profile_info(body: User, current_user: User, db: AsyncSession):
    """Updates the profile information of a user.

    :param body: The updated user information.
    :type body: User
    :param current_user: The current user.
    :type current_user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: The updated user object if successful, None otherwise.
    :rtype: User"""
    query = select(User).where(User.id == current_user.id)
    result = await db.execute(query)
    user = result.scalars().first()
    if user:
        if body.username:
            user.username = body.username
        if body.description:
            user.description = body.description
        await db.commit()
        await db.refresh(user)
        return user
    return None
