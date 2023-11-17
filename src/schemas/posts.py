from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, ClassVar
from datetime import datetime


class CommentBase(BaseModel):
    comment: str = Field(max_length=280)
    post_id: ClassVar[int]


class CommentsResponse(CommentBase):
    id: int
    post_id: int

    model_config = ConfigDict(from_attributes=True)


class TagModel(BaseModel):
    name: str = Field(max_length=25)


class TagResponse(TagModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class PostModel(BaseModel):
    title: str
    text: str
    tags: Optional[List[str]] = Field(max_items=5)


class PostCreate(PostModel):
    title: str
    text: str
    tags: Optional[List[str]]


class PostUpdate(BaseModel):
    title: Optional[str]
    text: Optional[str]
    tags: Optional[List[str]]


class PostResponse(PostModel):
    id: int
    created_at: datetime
    tags: List[TagResponse]

    class Config:
        from_attributes = True


class PostResponseOne(PostModel):
    id: int
    created_at: datetime
    tags: List[TagResponse]
    comments: List[CommentsResponse]

    class Config:
        from_attributes = True
