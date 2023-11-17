from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.rating import Rating, Post
from src.schemas.ratings import RatingModel
from src.database.models.users import User


async def get_rating_of_post(db: AsyncSession, post_id: int) -> int:
    likes = len((await db.execute(select(Rating).where(Rating.post_id==int(post_id), Rating.type=='LIKE'))).scalars().all())
    dislikes = len((await db.execute(select(Rating).where(Rating.post_id==int(post_id), Rating.type=='DISLIKE'))).scalars().all())
    return likes - dislikes


async def get_ratings_of_post(db: AsyncSession, post_id: int) -> List[Rating]:
    result = await db.execute(select(Rating).where(Rating.post_id==int(post_id)))
    return result.scalars().all()


async def get_ratings_of_user(db: AsyncSession, user_id: int) -> List[Rating]:
    result = await db.execute(select(Rating).where(Rating.user_id==int(user_id)))
    return result.scalars().all()


async def add_rating_for_post(db: AsyncSession, body: RatingModel, post_id) -> Rating:
    rating = Rating(**body.model_dump(), post_id=post_id)
    db.add(rating)
    await db.commit()
    await db.refresh(rating)
    return rating


async def get_post_by_id(db: AsyncSession, post_id: int) -> Post | None:
    return (await db.execute(select(Post).where(Post.id==post_id))).scalar_one_or_none()


async def is_user_author_of_post(db: AsyncSession, user_id: int, post_id: int) -> bool:
    post = (await db.execute(select(Post).where(Post.id==post_id))).scalar_one_or_none()
    if not post:
        return False
    return post.user_id == user_id


async def user_estimated_post(db: AsyncSession, user_id: int, post_id: int) -> bool:

    estimate_exists = (await db.execute(select(Rating).where(Rating.post_id==post_id, Rating.user_id==user_id))).scalar_one_or_none()
    return True if estimate_exists else False


async def remove_rating_for_post(db: AsyncSession, post_id: id, rating_id: id) -> Rating: 
    rating = (await db.execute(select(Rating).where(Rating.id==rating_id, Rating.post_id==post_id))).scalar_one_or_none()
    if not rating:
        return None
    await db.delete(rating)
    await db.commit()
    return rating


# relocate this function in user module
async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    return (await db.execute(select(User).where(User.id==user_id))).scalar_one_or_none()
