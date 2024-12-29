from fastapi import FastAPI
from fastapi.responses import FileResponse
from app.user import router as user_router
from app.catalog import router as catalog_router

app = FastAPI()


@app.get("/",tags=['Index HTML'])
def index():
    return FileResponse(r"/home/ramb1zzy/pyapp/templates/index.html")


app.include_router(router=user_router)
app.include_router(router=catalog_router)
