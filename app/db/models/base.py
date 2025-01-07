from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, DeclarativeBase, declared_attr, mapped_column


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr
    def __tablename__(self):
        return f"{self.__name__.lower()}s"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
