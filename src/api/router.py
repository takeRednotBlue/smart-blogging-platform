from fastapi import APIRouter

from src.api.auth import router as auth_router
from src.api.profile import router as profile_router

router = APIRouter(prefix="/v1")

router.include_router(auth_router)
router.include_router(profile_router)
