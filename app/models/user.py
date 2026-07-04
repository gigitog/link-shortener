"""SQLAlchemy-модель таблицы users."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.link import Link


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # relationship — «виртуальное» поле, не колонка в БД.
    # Позволяет получить все ссылки пользователя через user.links
    # без ручного написания JOIN-запроса.
    # back_populates связывает две стороны: User.links ↔ Link.owner
    links: Mapped[list[Link]] = relationship(back_populates="owner")
