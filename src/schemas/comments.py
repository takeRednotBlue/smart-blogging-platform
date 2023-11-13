from datetime import datetime
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field


class CommentBase(BaseModel):
    comment: str = Field(max_length=280)
    created_at: ClassVar[datetime]
    updated_at: ClassVar[datetime]
    post_id: ClassVar[int]
    user_id: ClassVar[int]


class CommentResponse(CommentBase):
    id: int
    created_at = datetime
    updated_at = datetime
    post_id = int
    user_id = int

    model_config = ConfigDict(from_attributes=True)
