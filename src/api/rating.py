from typing import List, Annotated

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_async_db
from src.database.models.users import User
from src.services.auth import auth_service
from src.repository import ratings as repository_ratings
from src.schemas.ratings import RatingModel, RatingResponse, PostRatingResponse, UserRatingResponse

router = APIRouter(prefix="/", tags=['ratings'])
async_db = Annotated[AsyncSession, Depends(get_async_db)]


@router.get('/post/{post_id}/rating')
async def read_rating_of_post(db: async_db, post_id, current_user: User=Depends(auth_service.get_current_user)) -> int:
    return await repository_ratings.get_rating_of_post(db, post_id)


@router.get('/post/{post_id}/ratings', response_model=List[PostRatingResponse])
async def read_ratings_of_post(db: async_db, post_id, current_user: User=Depends(auth_service.get_current_user)) -> List[PostRatingResponse]: 


@router.get('/user/{user_id}/ratings', response_model=List[UserRatingResponse])
async def read_ratings_of_user(db: async_db, user_id, current_user: User=Depends(auth_service.get_current_user)) -> List[UserRatingResponse]:
    return await repository_ratings.get_ratings_of_user(db, user_id)


@router.post('/post/{post_id}/ratings', response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
async def add_rating_for_post(body: RatingModel, db: async_db, post_id: int, current_user: User=Depends(auth_service.get_current_user)) -> RatingResponse: 

    post = await repository_ratings.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found.')
    
    user = await repository_ratings.get_user_by_id(db, body.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found.')
  
    is_user_author_of_post = await repository_ratings.is_user_author_of_post(db, body.user_id, post_id)
    if is_user_author_of_post:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User can't estimate his own post.")

    user_estimated_post = await repository_ratings.user_estimated_post(db, body.user_id, post_id)
    if user_estimated_post:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User has already estimated this post.")

    rating = await repository_ratings.add_rating_for_post(db, body, post_id)
    return rating


@router.delete('/post/{post_id}/ratings/{rating_id}', response_model=RatingResponse)
async def delete_rating(db: async_db, post_id: int, rating_id: int, current_user: User=Depends(auth_service.get_current_user)) -> RatingResponse:
    return await repository_ratings.remove_rating_for_post(db, post_id, rating_id)
