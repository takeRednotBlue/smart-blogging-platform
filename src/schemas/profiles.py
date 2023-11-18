from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.database.models.users import Roles


class Profile(BaseModel):
    username: str
    email: str
    description: Optional[str] = None


class ProfileResponse(Profile):
    created_at: datetime
    number_of_posts: int


class ProfileInfoResponse(Profile):
    roles: Roles
