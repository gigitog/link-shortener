"""Сервис авторизации: хэширование паролей и работа с JWT-токенами."""

from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app.config import settings


def hash_password(plain: str) -> str:
    """Превращает пароль в bcrypt-хэш. Необратимая операция —
    из хэша нельзя получить исходный пароль.

    bcrypt автоматически генерирует случайную «соль» (gensalt),
    поэтому два одинаковых пароля дают разные хэши.
    """
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Проверяет, соответствует ли пароль хэшу.
    bcrypt хэширует plain с той же солью, что зашита в hashed, и сравнивает."""
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Создаёт JWT (JSON Web Token).

    JWT состоит из трёх частей, разделённых точками:
      header.payload.signature

    - header: алгоритм (HS256) + тип (JWT)
    - payload: наши данные (data) + время истечения (exp)
    - signature: подпись всего вышеперечисленного через SECRET_KEY

    Сервер проверяет подпись при каждом запросе — если кто-то
    подменит payload, подпись не совпадёт → 401.
    """
    to_encode = data.copy()
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    to_encode["exp"] = datetime.now(UTC) + expires_delta
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    """Декодирует и проверяет JWT.

    Если токен просрочен (exp < сейчас) → ExpiredSignatureError.
    Если подпись невалидна → InvalidTokenError.
    """
    return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
