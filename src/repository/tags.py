from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database.models.tags import Tag
from src.schemas.tags import TagModel


async def get_tags(db: AsyncSession) ->List[Tag]:
    """
    ### Description
    Returns a list of all tags from the database.

    ### Query Parameters

    - `db` (**AsyncSession**): The database session.

    ### Returns
    - `List[Tag]`: A list of all tags.
    
    """
    result = await db.execute(select(Tag))
    return result.scalars().all()


async def create_tag(body: TagModel, db: AsyncSession) ->Tag:
    """
    ### Description
    Creates a new tag in the database.

    ### Query Parameters
    - `body` (**TagModel**): The tag model containing the name of the tag.
    - `db` (**AsyncSession**): The database session.

    ### Returns
    - `Tag`: The created tag.

    """
    tag = Tag(name=body.name)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag


async def get_tag(tagname: str, db: AsyncSession) ->Tag:
    """
    ### Description
    Retrieves a tag from the database based on the tag name.

    ### Query Parameters
    - `tagname` (**str**): The name of the tag to retrieve.
    - `db` (**AsyncSession**): The database session.

     ### Returns
    - `Tag`: The tag object.

    """
    result = await db.execute(select(Tag).where(Tag.name == tagname))
    return result.scalars().first()


async def update_tag(tagname: str, body: TagModel, db: AsyncSession) ->Tag:
    """
    ### Description
    Updates the name of a tag in the database.

    ### Query Parameters
    - `tagname` (**str**): The name of the tag to update.
    - `body` (**TagModel**): The updated tag information.
    - `db` (**AsyncSession**): The database session.

    ### Returns
    - `Tag`: The updated tag.
    
    """
    tag = (await db.execute(select(Tag).where(Tag.name == tagname))).scalars().first()

    if not tag:
        return None
    tag.name = body.name
    await db.commit()
    await db.refresh(tag)
    return tag
    


async def remove_tag(tagname: str, db: AsyncSession) ->Tag:
    """
    ### Description
    Removes a tag from the database.

    ### Query Parameters
    - `tagname` (**str**): The name of the tag to be removed.
    - `db` (**AsyncSession**): The database session.

    ### Returns
    - `Tag`: The removed tag, or None if the tag does not exist.
    
    """
    tag = (await db.execute(select(Tag).where(Tag.name == tagname))).scalars(
        ).first()
    if not tag:
        return None
    await db.delete(tag)
    await db.commit()
    return tag
