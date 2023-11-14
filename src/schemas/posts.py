from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List
from datetime import datetime


class TagModel(BaseModel):
    name: str = Field(max_length=25)


class TagResponse(TagModel):
    id: int

    class Config:
        from_attributes = True


class PostModel(BaseModel):
    title: str
    text: str
    tags: Optional[List[int]]


class PostCreate(PostModel):
    title: str
    text: str
    tags: Optional[List[int]]


class PostResponse(PostModel):
    id: int
    created_at: datetime
    tags: List[TagResponse]

    class Config:
        from_attributes = True


# class PostModel(BaseModel):
#     title: str
#     text: str
#     created_at: date
#     tags: Optional[List[str]] = Field(default_factory=list, max_items=5)
#     # user_id: int


class ResponsePost(BaseModel):
    id: int
    title: str
    text: str
    created_at: date
    tags: Optional[List[str]] = Field(default_factory=list, max_items=5)
    user_id: int

    class Config:
        from_attributes = True
