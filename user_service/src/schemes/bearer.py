from pydantic import BaseModel


class BearerResponse(BaseModel):
    access_token: str
    token_type: str
