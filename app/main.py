"""Точка входа FastAPI-приложения."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.middleware import LoggingMiddleware, RateLimitMiddleware
from app.routers import auth, health, links

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

# CORS — самым внешним слоем (добавлен последним), по двум причинам:
#   1. Ответ 429 от rate-limiter тоже должен получить CORS-заголовки,
#      иначе браузер в dev-режиме скроет тело ошибки от JS-кода фронта.
#   2. Preflight-запросы (OPTIONS) обрабатываются сразу здесь
#      и не тратят лимит rate-limiter'а.
# allow_credentials не включаем: токен передаётся в заголовке Authorization,
# а не в cookie, поэтому браузерные «credentials» не нужны.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(health.router)
app.include_router(links.router)
