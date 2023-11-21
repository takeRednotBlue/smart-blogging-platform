from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, constr

from src.database.models.users import Roles


class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=20)
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)


class UserDb(BaseModel):
    id: int
    username: str
    roles: Roles
    email: str
    created_at: datetime

    model_config: ConfigDict = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    username: Optional[constr(min_length=5, max_length=20)] = None
    description: Optional[constr(max_length=500)] = None


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created."


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr


class RoleRequest(BaseModel):
    role: Roles
