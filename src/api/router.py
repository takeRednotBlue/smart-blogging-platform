from fastapi import APIRouter
from src.api.autocomplete import autocomplete_router

router = APIRouter(prefix='/v1')

router.include_router(autocomplete_router)