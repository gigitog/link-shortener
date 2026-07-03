"""SQLAlchemy-модель таблицы links."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


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
    user_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, default=None)
