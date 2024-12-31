from fastapi import APIRouter
from app.catalog.views import router as catalog_router

router = APIRouter(prefix='/catalog', tags=['Catalog'])

router.include_router(router=catalog_router)
