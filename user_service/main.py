from contextlib import asynccontextmanager
from fastapi import FastAPI
from user_service.src.api.endpoints import router as user_router
from user_service.src.core.config import settings
from user_service.src.db.base import init_db

#
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     await init_db()
#     yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    # lifespan=lifespan,
)
app.include_router(router=user_router)
