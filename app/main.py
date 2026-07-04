"""Точка входа FastAPI-приложения."""

import logging

from fastapi import FastAPI

from app.middleware import LoggingMiddleware, RateLimitMiddleware
from app.routers import auth, links

# Настройка логирования — без этого logger.info() не выводит ничего,
# потому что по умолчанию уровень WARNING (т.е. info-сообщения игнорируются).
logging.basicConfig(level=logging.INFO)

# Таблицы теперь создаются/изменяются через Alembic-миграции,
# а не через create_all. Команда: uv run alembic upgrade head

app = FastAPI(
    title="Link Shortener",
    description="Сервис сокращения ссылок",
    version="0.1.0",
)

# Порядок важен: middleware выполняются СНИЗУ ВВЕРХ (стек).
# Rate limit проверяется первым (добавлен последним),
# затем логирование, затем запрос идёт в роутер.
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=30, window_seconds=60)

app.include_router(auth.router)
app.include_router(links.router)
