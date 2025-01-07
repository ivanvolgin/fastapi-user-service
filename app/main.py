from fastapi import FastAPI
from app.api.endpoints import api_v1 as router
from app.core.config import settings
from contextlib import asynccontextmanager
from app.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)


app.include_router(router=router)
