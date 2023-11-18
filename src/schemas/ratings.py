from pydantic import BaseModel, ConfigDict
from src.database.models.rating import RatingTypes
from src.schemas.users import UserResponse


class RatingModel(BaseModel):
    type: str
    user_id: int 


class RatingResponse(BaseModel):
    id: int
    type: RatingTypes
    post_id: int
    user_id: int 

    model_config: ConfigDict = ConfigDict(from_attributes=True)


class PostRatingResponse(BaseModel):
    id: int
    type: RatingTypes
    user_id: int 

    model_config: ConfigDict = ConfigDict(from_attributes=True)


class UserRatingResponse(BaseModel):
    id: int
    type: RatingTypes
    post_id: int 

    model_config: ConfigDict = ConfigDict(from_attributes=True)

#   # Delete this scheme
class PostModel(BaseModel):
    user_id: int 

    model_config: ConfigDict = ConfigDict(from_attributes=True)
