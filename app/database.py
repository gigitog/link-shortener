"""Подключение к PostgreSQL через SQLAlchemy (async)."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# Engine — это «пул соединений» с Postgres.
# echo=True — временно логирует SQL-запросы в консоль (удобно для отладки, уберём позже).
engine = create_async_engine(settings.database_url, echo=True)

# Фабрика сессий. Каждый запрос к API получает свою сессию (свою «транзакцию»).
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Базовый класс для всех SQLAlchemy-моделей. Все таблицы «наследуются» от него."""


async def get_db() -> AsyncSession:
    """
    Dependency для FastAPI: создаёт сессию БД на время одного запроса,
    закрывает после. Используется так:

        @router.get("/...")
        async def handler(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session() as session:
        yield session
