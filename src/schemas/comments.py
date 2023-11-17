from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CommentBase(BaseModel):
    comment: str = Field(max_length=280)


class CommentResponse(CommentBase):
    id: int
    updated_at: Optional[datetime]
    created_at: datetime
    post_id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)
