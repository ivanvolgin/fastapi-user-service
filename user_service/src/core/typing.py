from typing import Union, Callable
from pydantic import EmailStr
from sqlalchemy.orm import Mapped

StringType = Union[
    str,
    EmailStr,
    Mapped[str],
]