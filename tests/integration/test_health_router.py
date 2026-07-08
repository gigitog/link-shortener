"""Интеграционные тесты: /health (liveness) и /health/ready (readiness)."""

from httpx import AsyncClient

from app.database import get_db
from app.main import app


class TestHealth:
    async def test_ok(self, client: AsyncClient):
        """Liveness не трогает БД — отвечает 200 всегда."""
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


class TestHealthReady:
    async def test_ok(self, client: AsyncClient):
        """При живой БД (тестовая сессия из фикстуры) readiness отвечает 200."""
        resp = await client.get("/health/ready")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}

    async def test_db_unavailable(self, client: AsyncClient):
        """Если запрос к БД падает — readiness отвечает 503, а не 500.

        Сессия создаётся успешно (как в реальности — пул соединений жив),
        но конкретный запрос падает (например, оборвалась сеть до Postgres).
        """

        class BrokenSession:
            async def execute(self, *args, **kwargs):
                raise RuntimeError("db down")

        async def broken_get_db():
            yield BrokenSession()

        # Фикстура client сама очистит dependency_overrides после теста
        app.dependency_overrides[get_db] = broken_get_db
        resp = await client.get("/health/ready")

        assert resp.status_code == 503
