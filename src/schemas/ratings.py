from pydantic import BaseModel, ConfigDict
from src.database.models.rating import RatingTypes


class RatingModel(BaseModel):
    rating_type: str
    user_id: int


class RatingResponse(BaseModel):
    id: int
    rating_type: RatingTypes
    post_id: int
    user_id: int

    model_config: ConfigDict = ConfigDict(from_attributes=True)


class PostRatingResponse(BaseModel):
    id: int
    rating_type: RatingTypes
    user_id: int

    model_config: ConfigDict = ConfigDict(from_attributes=True)


class UserRatingResponse(BaseModel):
    id: int
    rating_type: RatingTypes
    post_id: int

    model_config: ConfigDict = ConfigDict(from_attributes=True)
