from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class CommentBase(BaseModel):
    comment: str = Field(max_length=280)
    post_id: int 


class CommentResponse(CommentBase):
    id: int

    model_config = ConfigDict(from_attributes = True)

    

# class UserModel(BaseModel):
#     username: str = Field(min_length=5, max_length=16)
#     email: str
#     password: str = Field(min_length=6, max_length=10)


# class UserDb(BaseModel):
#     id: int
#     username: str
#     email: str
#     created_at: datetime
#     avatar: str

#     class ConfigDict:
#         from_attributes = True


# class UserResponse(BaseModel):
#     user: UserDb
#     detail: str = "User successfully created"


# class TokenModel(BaseModel):
#     access_token: str
#     refresh_token: str
#     token_type: str = "bearer"


# class RequestEmail(BaseModel):
#     email: EmailStr
