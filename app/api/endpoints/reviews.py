from fastapi import APIRouter
from app.src.reviews.schemes import *
from fastapi import Form, Request, HTTPException
from fastapi.responses import FileResponse
import aiofiles

router = APIRouter()


@router.get("/reviews")
def reviews_form():
    return FileResponse("/reviews.html")


# @router.post("/reviews", response_model=ReviewResponse)
# async def make_review(
#     request: Request, name: str = Form(...), message: str = Form(...)
# ):
#     response = {
#         "name": name,
#         "message": message,
#         "status": "Your review has been successfully received. \n"
#         "Thanks for your feedback!.",
#     }
#
#     async def write_to_the_file(name, message):
#         async with aiofiles.open("/reviews.txt", "a") as f:
#             message = f"Name: {name}, " f"Message: {message}\n"
#             await f.write(message)
#
#     await write_to_the_file(name, message)
#
#     return ReviewResponse(**response)
