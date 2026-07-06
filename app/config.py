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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


# Единственный экземпляр настроек на всё приложение (синглтон).
# Импортируется как: from app.config import settings
settings = Settings()
