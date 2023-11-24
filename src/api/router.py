from fastapi import APIRouter

from src.api.auth import router as auth_router
from src.api.autocomplete import autocomplete_router
from src.api.illustrate import generate_picture_router
from src.api.posts import router as posts_router
from src.api.profile import router as profile_router
from src.api.tags import router as tag_router
from src.api.users import router as users_router

router = APIRouter(prefix="/v1")

router.include_router(posts_router)
router.include_router(auth_router)
router.include_router(profile_router)
router.include_router(autocomplete_router)
router.include_router(generate_picture_router)
router.include_router(tag_router)
router.include_router(users_router)
