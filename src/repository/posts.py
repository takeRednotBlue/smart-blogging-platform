from src.database.models.posts import Post, Tag
from sqlalchemy.orm import Session, joinedload
from src.schemas.posts import PostModel, PostCreate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


# async def create_post(body: PostModel, db: Session):
#     if body.tags:
#         body.tags = body.tags[:5]
#     post = Post(
#         title=body.title,
#         text=body.text,
#         created_at=body.created_at,
#         tags=body.tags,
#     )
#     db.add(post)
#     db.commit()
#     db.refresh(post)
#     return post


# async def create_post(body: PostCreate, db: Session):
#     db_post = Post(title=body.title, text=body.text)
#     db.add(db_post)
#     db.commit()
#     db.refresh(db_post)
#     return db_post


# async def create_post(post: Post, db: Session):
#     # Assuming Post is your SQLAlchemy model
#     db_post = Post(title=post.title, text=post.text)
#     # Add the new post to the database
#     db.add(db_post)
#     # Commit the changes to persist the new post
#     await db.commit()
#     # Refresh the instance to ensure we have the latest state from the database
#     db.refresh(db_post)
#     # Return the created post
#     return db_post


async def create_post(body: PostCreate, db: AsyncSession) -> Post:
    stmt = select(Tag).where(Tag.id.in_(body.tags))
    result = await db.execute(stmt)
    tags = result.scalars().all()
    post = Post(title=body.title, text=body.text, tags=tags)
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


async def get_posts(db: Session):
    posts = db.query(Post).all()
    return posts


async def get_post(post_id: int, db: Session):
    post = db.query(Post).filter(Post.id == post_id).options(joinedload(Post.comments)).first()
    return post


async def remove_post(post_id: int, db: Session):
    post = db.query(Post).filter_by(id=post_id).first()
    if post:
        db.delete(post)
        db.commit()
    return post


async def update_post(post_id: int, body: PostModel, db: Session):
    post = db.query(Post).filter_by(id=post_id).first()
    if not post:
        return None
    post.title = body.title
    post.text = body.text
    post.tags = body.tags
    db.commit()
    db.refresh(post)
    return post
