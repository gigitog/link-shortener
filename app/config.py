"""Настройки приложения, загружаемые из переменных окружения (.env файла)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    pydantic-settings автоматически читает переменные окружения (и .env файл).
    Имена полей = имена переменных в .env (регистр не важен).
    Если переменной нет ни в окружении, ни в .env — приложение упадёт при старте
    с понятной ошибкой, а не молча возьмёт пустую строку.
    """

    database_url: str
    secret_key: str = "dev-secret-not-for-production"
    base_url: str = "http://localhost:8000"

    # Параметры генерации коротких кодов
    short_code_length: int = 7

    # JWT-настройки
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Логировать ли SQL-запросы в консоль. Удобно при локальной отладке,
    # но в проде замусоривает логи и может «светить» данные — по умолчанию выключено.
    db_echo: bool = False

    # Origin'ы, которым разрешён CORS (через запятую). Нужно только для dev-режима,
    # когда фронт (vite, порт 5173) ходит к API (uvicorn, порт 8000) напрямую —
    # браузер считает это разными origin. В проде фронт и API за одним доменом
    # (Caddy делит пути), CORS не задействуется.
    # Строка, а не list[str]: для списков pydantic-settings требует JSON-синтаксис
    # в .env (CORS_ORIGINS=["..."]), это неудобно — проще split по запятой.
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        """CORS_ORIGINS из .env → список origin'ов без пустых элементов."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


# Единственный экземпляр настроек на всё приложение (синглтон).
# Импортируется как: from app.config import settings
settings = Settings()
