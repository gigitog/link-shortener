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
        # Верхняя граница = размер колонки short_code (VARCHAR(10)) — иначе
        # валидация пропустит значение, которое БД не сможет сохранить (ошибка 500).
        # Расширение до 30 отложено до этапа vanity-кодов (там будет миграция).
        if len(value) < 3 or len(value) > 10:
            raise ValueError("alias должен быть от 3 до 10 символов")
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


class LinkListResponse(BaseModel):
    """
    Ответ GET /links — страница списка с метаданными пагинации («конверт»).

    total нужен фронту, чтобы посчитать число страниц («Seite 2 von 5»).
    Конверт в теле (а не заголовок X-Total-Count) — самодокументируется
    в Swagger и не требует от клиента читать заголовки.
    """

    items: list[LinkResponse]
    total: int  # всего ссылок у пользователя (не только на этой странице)
    limit: int
    offset: int
