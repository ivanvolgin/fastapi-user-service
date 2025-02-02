from fastapi import APIRouter
from user_service.src.api.endpoints.register import router as register
from user_service.src.api.endpoints.auth import router as auth

router = APIRouter()
router.include_router(router=register, tags=["Register"])
router.include_router(router=auth, tags=["Auth"])
