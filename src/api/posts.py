from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.schemas.posts import (
    PostModel,
    PostResponse,
    PostResponseOne,
    PostUpdate,
)
from src.repository import posts as repository_posts
from src.database.db import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model=List[PostResponse])
async def get_all_posts(db: AsyncSession = Depends(get_async_db)):
    posts = await repository_posts.get_posts(db)
    return posts


@router.get(
    "/{post_id}",
    response_model=PostResponseOne,
)
async def get_post(post_id: int, db: Session = Depends(get_async_db)):
    post = await repository_posts.get_post(post_id, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.post("/", response_model=PostResponse, tags=["posts"])
async def create_post(body: PostModel, db: AsyncSession = Depends(get_async_db)):
    post = await repository_posts.create_post(body, db)
    return post


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(body: PostUpdate, post_id: int, db: AsyncSession = Depends(get_async_db)):
    post = await repository_posts.update_post(post_id, body, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.delete("/{post_id}", response_model=PostResponse)
async def delete_post(post_id: int, db: Session = Depends(get_async_db)):
    post = await repository_posts.remove_post(post_id, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post
