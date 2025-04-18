from typing import Union
from pydantic import BaseModel


class ErrorModel(BaseModel):
    detail: Union[str, dict[str, str]]
