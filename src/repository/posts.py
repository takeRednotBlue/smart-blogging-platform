from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.models.posts import Post
from src.database.models.tags import Tag
from src.database.models.users import User
from src.schemas.posts import PostCreate, PostUpdate


async def get_or_create_tag(tag_name: str, db: AsyncSession):
    """Creates a new tag in the database if it doesn't already exist, or retrieves an existing tag with the given name.

    :param tag_name: The name of the tag.
    :type tag_name: str
    :param db: The database session.
    :type db: AsyncSession
    :return: The created or retrieved tag.
    :rtype: Tag"""
    tag = (
        await db.execute(select(Tag).where(Tag.name == tag_name))
    ).scalar_one_or_none()
    if not tag:
        tag = Tag(name=tag_name)
        db.add(tag)
        await db.commit()
        await db.refresh(tag)
    return tag


async def create_post(body: PostCreate, user: User, db: AsyncSession) -> Post:
    """Creates a new post with the given information.

    :param body: The data for creating the post.
    :type body: PostCreate
    :param user: The user creating the post.
    :type user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: The created post.
    :rtype: Post"""
    tags = [(await get_or_create_tag(tag, db)) for tag in body.tags]
    post = Post(title=body.title, text=body.text, user_id=user.id)
    post.tags = tags
    db.add(post)
    await db.commit()
    await db.refresh(post, ["tags"])
    return post


async def update_post(
    post_id: int, user: User, body: PostUpdate, db: AsyncSession
):
    """Updates a post with the given post ID, user, body, and database session.

    :param post_id: The ID of the post to update.
    :type post_id: int
    :param user: The user who is updating the post.
    :type user: User
    :param body: The updated post data.
    :type body: PostUpdate
    :param db: The database session.
    :type db: AsyncSession
    :return: The updated post if it exists and the user has permission to update it, otherwise None.
    :rtype: Post or None"""
    statement = (
        select(Post)
        .where(and_(Post.id == post_id, Post.user_id == user.id))
        .options(selectinload(Post.tags))
    )
    result_post = await db.execute(statement)
    post_f = result_post.scalar_one_or_none()
    if post_f and post_f.user_id == user.id:
        tags = [(await get_or_create_tag(tag, db)) for tag in body.tags]
        post_f.title = body.title
        post_f.text = body.text
        post_f.tags = tags
        post_f.user = user
        await db.commit()
        await db.refresh(post_f, ["tags"])
        return post_f
    else:
        return None


async def remove_post(post_id: int, user: User, db: AsyncSession):
    """Removes a post from the database.

    :param post_id: The ID of the post to be removed.
    :type post_id: int
    :param user: The user who is removing the post.
    :type user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: The removed post if it exists and the user has permission to remove it, otherwise None.
    :rtype: Post or None"""
    post = select(Post).where(
        and_(Post.id == post_id, Post.user_id == user.id)
    )
    post = await db.execute(post)
    post_result = post.scalars().first()
    if post_result and post_result.user_id == user.id:
        await db.delete(post_result)
        await db.commit()
        return post_result
    else:
        return None


async def get_posts(db: AsyncSession):
    """Retrieves all posts from the database.

    :param db: The database session.
    :type db: AsyncSession
    :return: A list of all posts.
    :rtype: list[Post]"""
    posts_query = select(Post).options(selectinload(Post.tags))
    result = await db.execute(posts_query)
    posts_all = result.scalars().all()
    return posts_all


async def get_post(post_id: int, db: AsyncSession):
    """Returns a post with the specified post_id from the database.

    :param post_id: The ID of the post.
    :type post_id: int
    :param db: The database session.
    :type db: AsyncSession
    :return: The post with the specified post_id.
    :rtype: Post"""
    post_query = (
        select(Post)
        .options(selectinload(Post.tags), selectinload(Post.comments))
        .where(Post.id == post_id)
    )
    result = await db.execute(post_query)
    post = result.scalar()
    return post
