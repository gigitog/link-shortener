"""Pydantic-схемы для пользователей и JWT-токенов."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator


class UserCreate(BaseModel):
    """Тело запроса POST /auth/register.

    EmailStr — тип Pydantic, который проверяет формат email
    (наличие @, валидный домен и т.д.). Невалидный → 422.
    """

    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("пароль должен быть не менее 8 символов")
        return value


class UserResponse(BaseModel):
    """Ответ API с данными пользователя.

    Важно: hashed_password НЕ включён — нельзя отдавать хэш наружу,
    даже если его невозможно расшифровать напрямую (атаки по словарю).
    """

    id: int
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """Ответ API при успешном логине.

    access_token — JWT-строка, которую клиент передаёт в заголовке
    Authorization: Bearer <token> при каждом запросе.
    token_type — всегда "bearer" (стандарт OAuth2).
    """

    access_token: str
    token_type: str = "bearer"
