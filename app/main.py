"""Точка входа FastAPI-приложения."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app.logging_config import setup_logging
from app.middleware import LoggingMiddleware, RateLimitMiddleware
from app.routers import auth, health, links

# JSON-логи вместо logging.basicConfig — см. app/logging_config.py.
setup_logging()

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

# Метрики Prometheus. instrument() добавляет ещё один middleware через
# add_middleware — добавлен последним, значит (см. правило выше) выполняется
# ПЕРВЫМ, раньше даже CORS и rate-limit: попадают в статистику вообще все
# запросы, включая те, что потом отклонит лимитер (429).
# expose() регистрирует сам GET /metrics — до include_router(links.router),
# чтобы этот путь не перехватил catch-all "/{short_code}".
#
# Библиотека сама решает те же задачи, что мы делали руками в PR3:
# - шаблон роута вместо сырого пути (иначе — взрыв кардинальности);
# - для путей без совпавшего роута — общая метка handler="none"
#   (should_group_untemplated=True по умолчанию);
# - статусы группируются в 2xx/4xx/5xx (should_group_status_codes=True) —
#   иначе на каждый уникальный код был бы свой ряд.
Instrumentator().instrument(app).expose(app)

app.include_router(auth.router)
app.include_router(health.router)
app.include_router(links.router)
