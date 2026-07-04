"""SQLAlchemy-модель таблицы links."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class Link(Base):
    __tablename__ = "links"

    # Составной уникальный ключ: один и тот же short_code может существовать
    # на разных доменах (мультидоменность, реализуем полностью на этапе K8s).
    __table_args__ = (UniqueConstraint("domain", "short_code"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    domain: Mapped[str] = mapped_column(String(255))
    short_code: Mapped[str] = mapped_column(String(10))
    original_url: Mapped[str] = mapped_column(Text)
    clicks_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # ForeignKey — ограничение на уровне БД: user_id может содержать
    # только значения, которые реально есть в users.id (или NULL).
    # Postgres не даст вставить несуществующий user_id.
    user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=True, default=None
    )

    # relationship — обратная сторона связи User.links.
    # Позволяет получить владельца ссылки через link.owner
    owner: Mapped[User | None] = relationship(back_populates="links")
