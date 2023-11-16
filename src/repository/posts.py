from src.database.models.posts import Post, Tag
from sqlalchemy.orm import Session, selectinload
from src.schemas.posts import PostModel, PostCreate, PostUpdate
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException


async def get_or_create_tag(tag_name: str, db: AsyncSession):
    tag = (await db.execute(select(Tag).where(Tag.name == tag_name))).scalar_one_or_none()
    if not tag:
        tag = Tag(name=tag_name)
        print(tag)
        db.add(tag)
        await db.commit()
        await db.refresh(tag)
    return tag


async def create_post(body: PostCreate, db: AsyncSession) -> Post:
    # tag = Tag(name="test")
    # db.add(tag)
    # await db.commit()
    # stmt = select(Tag).where(Tag.id.in_(body.tags))
    # result = await db.execute(stmt)
    # tags = result.scalars().all()
    tags = [await get_or_create_tag(tag, db) for tag in body.tags]
    post = Post(title=body.title, text=body.text)
    post.tags = tags
    db.add(post)
    await db.commit()
    await db.refresh(post, ["tags"])
    return post


async def update_post(post_id: int, body: PostUpdate, db: AsyncSession):
    statement = select(Post).where(Post.id == post_id).options(selectinload(Post.tags))
    result_post = await db.execute(statement)
    post_f = result_post.scalar_one_or_none()
    # await db.refresh(post_f, ["tags"])
    if post_f:
        stmt = select(Tag).where(Tag.id.in_(body.tags))
        result = await db.execute(stmt)
        tags = result.scalars().all()
        post_f.title = body.title
        post_f.text = body.text
        post_f.tags = tags
        await db.commit()
        await db.refresh(post_f, ["tags"])
        return post_f


async def remove_post(post_id: int, db: AsyncSession):
    post = select(Post).where(Post.id == post_id)
    post = await db.execute(post)
    post_result = post.scalars().first()
    if post_result:
        await db.delete(post_result)
        await db.commit()
    return post_result


async def get_posts(db: AsyncSession):
    # Use selectinload to eagerly load related tags
    posts_query = select(Post).options(selectinload(Post.tags))

    result = await db.execute(posts_query)
    posts_all = result.scalars().all()

    return posts_all


async def get_post(post_id: int, db: AsyncSession):
    post_query = (
        select(Post)
        .options(selectinload(Post.tags), selectinload(Post.comments))
        .where(Post.id == post_id)
    )
    result = await db.execute(post_query)
    post = result.scalar()

    return post
