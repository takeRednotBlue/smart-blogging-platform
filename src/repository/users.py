from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.users import User, Roles
from src.schemas.users import UserModel, RoleRequest


async def get_user_by_email(email: str, db: AsyncSession) -> User | None:
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_user(body: UserModel, db: AsyncSession) -> User:
    new_user = User(**body.model_dump())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(
    user: User, refresh_token: str, db: AsyncSession
) -> None:
    user.refresh_token = refresh_token
    db.add(user)
    await db.commit()


async def confirmed_email(email: str, db: AsyncSession) -> None:
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def assign_role_to_user(
    user_id: int, body: RoleRequest, db: AsyncSession
) -> None | Roles:
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
