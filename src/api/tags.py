from typing import Union, List

from fastapi import FastAPI, Path, APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.db import get_async_db
# from src.database.auth import auth_service
from src.repository import tags as repository_tags
from src.database.models.tags import Tag
from src.schemas.tags import TagModel, TagResponse

router = APIRouter(tags=["tags"])


@router.get("/tags/", 
            response_model=List[TagResponse])
async def read_tags(db: Session = Depends(get_async_db)) -> List[TagResponse]:
    return await repository_tags.get_tags(db)



@router.post("/tags/", 
             response_model=TagModel, 
             status_code=status.HTTP_201_CREATED)
async def create_tag(body: TagModel, 
                     db: Session = Depends(get_async_db)) -> Tag:
      
    tag = await repository_tags.get_tag(body.name, db)
    if tag:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tag already exists")
    return await repository_tags.create_tag(body, db)



@router.get("/tags/{tagname}", 
            response_model=TagResponse)
async def read_tag(tagname: str = Path(description="The name of the tag to get"),
                   db: Session = Depends(get_async_db)) -> Tag:
    tag = await repository_tags.get_tag(tagname, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag



@router.put("/tags/{tagname}", 
            response_model=TagResponse)
async def update_tag(body: TagModel, 
                         tagname: str = Path(description="The name of the tag to put"),
                         db: Session = Depends(get_async_db)) -> Tag:
 
    tag = await repository_tags.update_tag(tagname, body, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag


@router.delete("/tags/{tagname}", 
               response_model=TagResponse)
async def remove_tag(tagname: str = Path(description="The name of the tag to delete"),
                     db: Session = Depends(get_async_db)) -> Tag:
    tag = await repository_tags.remove_tag(tagname, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag

