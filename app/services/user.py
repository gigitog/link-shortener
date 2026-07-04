"""Бизнес-логика работы с пользователями."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.auth import hash_password, verify_password


async def create_user(db: AsyncSession, email: str, password: str) -> User:
    """Регистрирует нового пользователя.

    Хэширует пароль (в БД хранится только хэш, не сам пароль).
    Бросает ValueError, если email уже занят.
    """
    user = User(email=email, hashed_password=hash_password(password))
    db.add(user)
    try:
        await db.commit()
        await db.refresh(user)
        return user
    except IntegrityError:
        await db.rollback()
        raise ValueError("пользователь с таким email уже существует") from None


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Находит пользователя по email."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    """Проверяет email + пароль. Возвращает User если всё ок, None если нет.

    Важно: даже если пользователь не найден, мы не говорим об этом
    напрямую — возвращаем None в обоих случаях (неверный email / неверный пароль).
    Это не даёт атакующему понять, какие email зарегистрированы в системе.
    """
    user = await get_user_by_email(db, email)
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
