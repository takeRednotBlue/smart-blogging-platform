from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.users import Roles, User
from src.schemas.users import RoleRequest, UserModel


async def get_user_by_email(email: str, db: AsyncSession) -> (User | None):
    """Returns a user object based on the provided email address.

    :param email: The email address of the user.
    :type email: str
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :return: The user object if found, otherwise None.
    :rtype: User | None"""
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_user(body: UserModel, db: AsyncSession) -> User:
    """Creates a new user in the database.

    :param body: The user model containing the user data.
    :type body: UserModel
    :param db: The database session.
    :type db: AsyncSession
    :return: The newly created user.
    :rtype: User"""
    new_user = User(**body.model_dump())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, refresh_token: str, db: AsyncSession) -> None:
    """Updates the refresh token of a user in the database.

    :param user: The user object.
    :type user: User
    :param refresh_token: The new refresh token.
    :type refresh_token: str
    :param db: The database session.
    :type db: AsyncSession
    :return: None
    :rtype: None"""
    user.refresh_token = refresh_token
    db.add(user)
    await db.commit()


async def confirmed_email(email: str, db: AsyncSession) -> None:
    """Updates the confirmation status of a user's email.

    :param email: The email address of the user.
    :type email: str
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :return: None
    :rtype: None"""
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def assign_role_to_user(
    user_id: int, body: RoleRequest, db: AsyncSession
) -> (None | Roles):
    """Assigns a role to a user.

    :param user_id: The ID of the user.
    :type user_id: int
    :param body: The role request object.
    :type body: RoleRequest
    :param db: The database session.
    :type db: AsyncSession
    :return: The roles assigned to the user.
    :rtype: None or Roles"""
    user = (
        await db.execute(select(User).where(User.id == user_id))
    ).scalar_one_or_none()
    if not user:
        return None
    user.roles = body.role
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user.roles
