"""Точка входа FastAPI-приложения."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import links


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan — код, который выполняется при старте и остановке приложения.

    При старте: создаём таблицы в БД (если их ещё нет).
    Это временное решение для MVP — на этапе миграций (Alembic) уберём.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Link Shortener",
    description="Сервис сокращения ссылок",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(links.router)
