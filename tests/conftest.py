"""Глобальные фикстуры для тестов.

Ключевые решения:
- Реальный PostgreSQL (контейнер на порту 5433) — тестируем с тем же движком, что в проде.
- Изоляция тестов через SAVEPOINT: каждый тест работает внутри вложенной транзакции,
  которая откатывается после завершения. Таблицы создаются один раз за сессию.
- app.dependency_overrides[get_db] подставляет тестовую сессию вместо боевой.
"""

import os

# Устанавливаем DATABASE_URL до импорта app (settings читает .env при первом импорте)
os.environ["DATABASE_URL"] = "postgresql+asyncpg://app:app@localhost:5433/link_shortener_test"

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.database import Base, get_db
from app.main import app
from app.middleware import RateLimitMiddleware
from app.services.auth import create_access_token
from app.services.user import create_user

TEST_DATABASE_URL = os.environ["DATABASE_URL"]


@pytest.fixture(scope="session")
async def engine():
    """Создаёт движок к тестовой БД, таблицы — в начале, удаляет — в конце."""
    eng = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield eng

    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await eng.dispose()


@pytest.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession]:
    """Сессия внутри транзакции с SAVEPOINT → rollback после теста.

    join_transaction_mode="create_savepoint" — при вызове session.commit()
    внутри сервисов SQLAlchemy делает RELEASE SAVEPOINT, а не настоящий COMMIT.
    Это позволяет откатить ВСЁ в конце теста через rollback внешней транзакции.
    """
    async with engine.connect() as conn:
        trans = await conn.begin()
        session = AsyncSession(
            bind=conn,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )

        yield session

        await session.close()
        await trans.rollback()


def _find_rate_limiter(asgi_app) -> RateLimitMiddleware | None:
    """Проходит по цепочке middleware и находит RateLimitMiddleware."""
    current = asgi_app
    while current:
        if isinstance(current, RateLimitMiddleware):
            return current
        current = getattr(current, "app", None)
    return None


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient]:
    """HTTP-клиент, привязанный к тестовой сессии БД."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Сброс rate limiter между тестами — иначе лимит накапливается
    rate_limiter = _find_rate_limiter(app.middleware_stack)
    if rate_limiter:
        rate_limiter.requests.clear()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def sample_user(db_session: AsyncSession):
    """Предсозданный пользователь в тестовой БД."""
    return await create_user(db_session, "test@example.com", "securepass123")


@pytest.fixture
async def auth_headers(sample_user) -> dict[str, str]:
    """Заголовки авторизации с валидным JWT для sample_user."""
    token = create_access_token(data={"sub": sample_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def auth_client(client: AsyncClient, auth_headers: dict[str, str]) -> AsyncClient:
    """HTTP-клиент с авторизацией (токен в заголовках)."""
    client.headers.update(auth_headers)
    return client
