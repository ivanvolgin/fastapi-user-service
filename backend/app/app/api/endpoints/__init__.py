from fastapi import APIRouter
from fastapi.responses import FileResponse
from app.api.endpoints.user import router as user_router

api_v1 = APIRouter(prefix="/api/v1")


@api_v1.get("/")
def index():
    return FileResponse(
        r"/Users/ivanvolgin/pyprojects/pyapp_FastAPI/backend/app/templates/index.html"
    )


#
# api_v1.include_router(router=catalog_router, prefix="/catalog", tags=["Catalog"])
# api_v1.include_router(router=reviews_router, prefix="/reviews", tags=["Reviews"])
api_v1.include_router(router=user_router, prefix="/user", tags=["User"])

__all__ = ("api_v1",)
