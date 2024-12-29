from fastapi import APIRouter
from app.user.views import router as users_router
from app.user.auth import router as auth_router

router = APIRouter()

router.include_router(router=users_router)
router.include_router(router=auth_router)