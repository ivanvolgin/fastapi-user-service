from pydantic import BaseModel

class Review(BaseModel):
    name: str
    message: str

class ReviewResponse(Review):
    status: str
