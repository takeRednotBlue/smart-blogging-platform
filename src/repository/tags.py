from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.tags import Tag
from src.schemas.tags import TagModel


async def get_tags(db: AsyncSession) -> List[Tag]:
    """Returns a list of all tags from the database.

    :param db: The database session.
    :type db: AsyncSession
    :return: A list of all tags.
    :rtype: List[Tag]"""
    result = await db.execute(select(Tag))
    return result.scalars().all()


async def create_tag(body: TagModel, db: AsyncSession) -> Tag:
    """Creates a new tag in the database.

    :param body: The tag model containing the name of the tag.
    :type body: TagModel
    :param db: The database session.
    :type db: AsyncSession
    :return: The created tag.
    :rtype: Tag"""
    tag = Tag(name=body.name)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag


async def get_tag(tagname: str, db: AsyncSession) -> Tag:
    """Retrieves a tag from the database based on the tag name.

    :param tagname: The name of the tag to retrieve.
    :type tagname: str
    :param db: The asynchronous session to use for the database operations.
    :type db: AsyncSession
    :return: The tag object with the specified name, or None if no tag is found.
    :rtype: Tag"""
    result = await db.execute(select(Tag).where(Tag.name == tagname))
    return result.scalars().first()


async def update_tag(tagname: str, body: TagModel, db: AsyncSession) -> Tag:
    """Updates the name of a tag in the database.

    :param tagname: The name of the tag to update.
    :type tagname: str
    :param body: The updated tag information.
    :type body: TagModel
    :param db: The database session.
    :type db: AsyncSession
    :return: The updated tag.
    :rtype: Tag"""
    tag = (
        (await db.execute(select(Tag).where(Tag.name == tagname)))
        .scalars()
        .first()
    )
    if not tag:
        return None
    tag.name = body.name
    await db.commit()
    await db.refresh(tag)
    return tag


async def remove_tag(tagname: str, db: AsyncSession) -> Tag:
    """Removes a tag from the database.

    :param tagname: The name of the tag to be removed.
    :type tagname: str
    :param db: The database session.
    :type db: AsyncSession
    :return: The removed tag, or None if the tag does not exist.
    :rtype: Tag"""
    tag = (
        (await db.execute(select(Tag).where(Tag.name == tagname)))
        .scalars()
        .first()
    )
    if not tag:
        return None
    await db.delete(tag)
    await db.commit()
    return tag
