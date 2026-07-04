"""Точка входа FastAPI-приложения."""

from fastapi import FastAPI

from app.routers import auth, links

# Таблицы теперь создаются/изменяются через Alembic-миграции,
# а не через create_all. Команда: uv run alembic upgrade head

app = FastAPI(
    title="Link Shortener",
    description="Сервис сокращения ссылок",
    version="0.1.0",
)

app.include_router(auth.router)
app.include_router(links.router)
