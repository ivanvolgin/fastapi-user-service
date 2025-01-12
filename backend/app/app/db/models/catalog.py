from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.db.models import Base


class Product(Base):
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column("desc", String(255))
    price: Mapped[float] = mapped_column(Float, nullable=False)
