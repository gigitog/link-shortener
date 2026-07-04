"""Все модели импортируются здесь, чтобы Alembic видел их через Base.metadata."""

from app.models.link import Link
from app.models.user import User

__all__ = ["Link", "User"]
