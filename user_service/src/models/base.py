import uuid
from sqlalchemy import ForeignKey
from sqlalchemy.orm import declared_attr, Mapped, mapped_column, DeclarativeBase
from sqlalchemy.dialects.postgresql import UUID


class Base(DeclarativeBase):
    pass


class BaseUserTable(Base):
    __abstract__ = True
    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)


class BaseOAuthAccountTable(Base):
    __abstract__ = True
    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)

    @declared_attr
    def user_id(self) -> Mapped[UUID]:
        return mapped_column(
            UUID, ForeignKey("users.id", ondelete="cascade"), nullable=False
        )
