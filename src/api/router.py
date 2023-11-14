from fastapi import APIRouter

from src.api.posts import router as posts_router

router = APIRouter(prefix="/v1")

router.include_router(posts_router)
