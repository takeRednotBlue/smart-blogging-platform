from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models.rating import Rating
from src.database.models.posts import Post
from src.schemas.ratings import RatingModel
from src.database.models.users import User


async def get_rating_of_post(db: AsyncSession, post_id: int) -> int:
    """Calculates the rating of a post based on the number of likes and dislikes.

    :param db: The database session.
    :type db: AsyncSession
    :param post_id: The ID of the post.
    :type post_id: int
    :return: The rating of the post (number of likes minus number of dislikes).
    :rtype: int"""
    likes = len((await db.execute(select(Rating).where(Rating.post_id ==
        int(post_id), Rating.rating_type == 'LIKE'))).scalars().all())
    dislikes = len((await db.execute(select(Rating).where(Rating.post_id ==
        int(post_id), Rating.rating_type == 'DISLIKE'))).scalars().all())
    return likes - dislikes


async def get_ratings_of_post(db: AsyncSession, post_id: int) -> List[Rating]:
    """Returns a list of ratings for a given post.

    :param db: The database session.
    :type db: AsyncSession
    :param post_id: The ID of the post.
    :type post_id: int
    :return: A list of ratings for the post.
    :rtype: List[Rating]"""
    result = await db.execute(select(Rating).where(Rating.post_id == int(
        post_id)))
    return result.scalars().all()


async def get_ratings_of_user(db: AsyncSession, user_id: int) -> List[Rating]:
    """Returns a list of ratings for a given user.

    :param db: The asynchronous session to the database.
    :type db: AsyncSession
    :param user_id: The ID of the user.
    :type user_id: int
    :return: A list of ratings for the user.
    :rtype: List[Rating]"""
    result = await db.execute(select(Rating).where(Rating.user_id == int(
        user_id)))
    return result.scalars().all()


async def add_rating_for_post(db: AsyncSession, body: RatingModel, post_id
    ) -> Rating:
    """Adds a rating for a post.

    :param db: The database session.
    :type db: AsyncSession
    :param body: The rating model.
    :type body: RatingModel
    :param post_id: The ID of the post.
    :type post_id: int
    :return: The created rating.
    :rtype: Rating"""
    rating = Rating(**body.model_dump(), post_id=post_id)
    db.add(rating)
    await db.commit()
    await db.refresh(rating)
    return rating


async def get_post_by_id(db: AsyncSession, post_id: int) -> (Post | None):
    """Returns a post from the database based on the given post ID.

    :param db: The asynchronous session to the database.
    :type db: AsyncSession
    :param post_id: The ID of the post to retrieve.
    :type post_id: int
    :return: The post with the given ID, or None if no post is found.
    :rtype: Post | None"""
    print((await db.execute(select(Post).where(Post.id == int(post_id)))
        ).scalar_one_or_none())
    return (await db.execute(select(Post).where(Post.id == int(post_id)))
        ).scalar_one_or_none()


async def is_user_author_of_post(db: AsyncSession, user_id: int, post_id: int
    ) -> bool:
    """Checks if a user is the author of a post.

    :param db: The database session.
    :type db: AsyncSession
    :param user_id: The ID of the user.
    :type user_id: int
    :param post_id: The ID of the post.
    :type post_id: int
    :return: True if the user is the author of the post, False otherwise.
    :rtype: bool"""
    post = (await db.execute(select(Post).where(Post.id == post_id))
        ).scalar_one_or_none()
    if not post:
        return False
    return post.user_id == user_id


async def user_estimated_post(db: AsyncSession, user_id: int, post_id: int
    ) -> bool:
    """Checks if a user has estimated a post.

    :param db: The database session.
    :type db: AsyncSession
    :param user_id: The ID of the user.
    :type user_id: int
    :param post_id: The ID of the post.
    :type post_id: int
    :return: True if the user has estimated the post, False otherwise.
    :rtype: bool"""
    estimate_exists = (await db.execute(select(Rating).where(Rating.post_id ==
        post_id, Rating.user_id == user_id))).scalar_one_or_none()
    return True if estimate_exists else False


async def remove_rating_for_post(db: AsyncSession, post_id: int, rating_id: int
    ) -> Rating:
    """Removes a rating for a post.

    :param db: The asynchronous session to the database.
    :type db: AsyncSession
    :param post_id: The ID of the post.
    :type post_id: int
    :param rating_id: The ID of the rating.
    :type rating_id: int
    :return: The removed rating or None if the rating does not exist.
    :rtype: Rating or None"""
    rating = (await db.execute(select(Rating).where(Rating.id == rating_id,
        Rating.post_id == int(post_id)))).scalar_one_or_none()
    if not rating:
        return None
    await db.delete(rating)
    await db.commit()
    return rating


async def rating_exists_for_post(db: AsyncSession, post_id: int, rating_id: int
    ) -> (Rating | None):
    """Checks if a rating exists for a post.

    :param db: The database session.
    :type db: AsyncSession
    :param post_id: The ID of the post.
    :type post_id: int
    :param rating_id: The ID of the rating.
    :type rating_id: int
    :return: The rating if it exists, otherwise None.
    :rtype: Rating | None"""
    return (await db.execute(select(Rating).where(Rating.id == rating_id, 
        Rating.post_id == post_id))).scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> (User | None):
    """Returns a user from the database based on the given user ID.

    :param db: The asynchronous session to the database.
    :type db: AsyncSession
    :param user_id: The ID of the user to retrieve.
    :type user_id: int
    :return: The user with the specified ID, or None if no user is found.
    :rtype: User | None"""
    return (await db.execute(select(User).where(User.id == int(user_id)))
        ).scalar_one_or_none()
