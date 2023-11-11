from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import select


from src.database.models.tags import Tag
from src.schemas.tags import TagModel


async def get_tags(db: Session) -> List[Tag]:
    result = await db.execute(select(Tag))
    return result.scalars()


async def create_tag(body: TagModel, db: Session) -> Tag:  
    tag = Tag(name=body.name)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag


async def get_tag(tagname: str, db: Session) -> Tag:  
    result = await db.execute(select(Tag).where(Tag.name == tagname))
    return result.scalars().first()



async def update_tag(tagname: str, body: TagModel, db: Session) -> Tag:
    tag = (await db.execute(select(Tag).where(Tag.name == tagname))).scalars().first()
    if not tag:
        return None

    tag.name = body.name
    await db.commit()
    return tag


async def remove_tag(tagname: str, db: Session) -> Tag:
    tag = (await db.execute(select(Tag).where(Tag.name == tagname))).scalars().first()
    if not tag:
        return None
    
    await db.delete(tag)
    await db.commit()
    return tag

