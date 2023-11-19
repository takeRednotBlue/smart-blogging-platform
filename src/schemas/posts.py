from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, ClassVar
from datetime import datetime
from src.schemas.tags import TagResponse


class CommentBase(BaseModel):
    comment: str = Field(max_length=280)
    post_id: ClassVar[int]


class CommentsResponse(CommentBase):
    id: int
    post_id: int

    model_config = ConfigDict(from_attributes=True)


class PostModel(BaseModel):
    title: str
    text: str
    tags: Optional[List[str]] = Field(default=None, max_items=5)


class PostCreate(PostModel):
    pass


class PostUpdate(BaseModel):
    title: Optional[str]
    text: Optional[str]
    tags: List[str] = Field(default=None, max_items=5)


class PostResponse(PostModel):
    id: int
    created_at: datetime
    tags: List[TagResponse]

    class Config:
        model_config = ConfigDict(from_attributes=True)


class PostResponseOne(PostModel):
    id: int
    created_at: datetime
    tags: List[TagResponse]
    comments: List[CommentsResponse]

    class Config:
        model_config = ConfigDict(from_attributes=True)