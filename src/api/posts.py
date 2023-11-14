from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.schemas.posts import ResponsePost, PostModel, PostResponse
from src.repository import posts as repository_posts
from src.database.db import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/all", response_model=List[ResponsePost])
async def get_all_posts(db: Session = Depends(get_async_db)):
    posts = await repository_posts.get_posts(db)
    return posts


@router.get(
    "/{post_id}",
    response_model=ResponsePost,
)
async def get_post(post_id: int, db: Session = Depends(get_async_db)):
    post = await repository_posts.get_post(post_id, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.post("/addpost", response_model=PostResponse, tags=["posts"])
async def create_post(body: PostModel, db: AsyncSession = Depends(get_async_db)):
    post = await repository_posts.create_post(body, db)
    return post


@router.put("/{post_id}", response_model=ResponsePost)
async def update_post(body: PostModel, post_id: int, db: Session = Depends(get_async_db)):
    post = await repository_posts.update_post(post_id, body, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.delete("/{post_id}", response_model=ResponsePost)
async def delete_post(post_id: int, db: Session = Depends(get_async_db)):
    post = await repository_posts.remove_post(post_id, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post
