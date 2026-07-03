"""Pydantic-схемы для валидации запросов и формирования ответов."""

import re
from datetime import datetime

from pydantic import BaseModel, HttpUrl, field_validator

# Допустимые символы для custom alias: буквы, цифры, дефис, подчёркивание
ALIAS_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")


class LinkCreate(BaseModel):
    """Тело запроса POST /links."""

    # HttpUrl — встроенный тип Pydantic: проверяет, что строка — валидный URL
    # с протоколом (http/https). Невалидный URL → автоматическая 422 ошибка.
    original_url: HttpUrl

    # Пользовательский alias (опционально). Если не передан — генерируем случайный.
    custom_alias: str | None = None

    @field_validator("custom_alias")
    @classmethod
    def validate_custom_alias(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if len(value) < 3 or len(value) > 30:
            raise ValueError("alias должен быть от 3 до 30 символов")
        if not ALIAS_PATTERN.match(value):
            raise ValueError("alias может содержать только буквы, цифры, дефис и подчёркивание")
        return value


class LinkResponse(BaseModel):
    """Ответ API при создании ссылки и при получении информации о ней."""

    id: int
    short_code: str
    original_url: str
    short_url: str  # полный URL для пользователя: https://go.faiuk.me/abc1234
    clicks_count: int
    created_at: datetime

    model_config = {"from_attributes": True}
