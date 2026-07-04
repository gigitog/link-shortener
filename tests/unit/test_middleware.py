"""Тесты rate-limit middleware."""

from unittest.mock import AsyncMock, patch

from app.middleware import RateLimitMiddleware


async def _make_scope(client_ip: str = "127.0.0.1") -> dict:
    """Создаёт минимальный ASGI HTTP scope для тестирования."""
    return {
        "type": "http",
        "method": "GET",
        "path": "/test",
        "client": (client_ip, 12345),
        "headers": [],
    }


class TestRateLimitMiddleware:
    async def test_allows_under_threshold(self):
        """Запросы ниже лимита проходят."""
        inner_app = AsyncMock()
        middleware = RateLimitMiddleware(inner_app, max_requests=5, window_seconds=60)
        scope = await _make_scope()

        for _ in range(5):
            await middleware(scope, AsyncMock(), AsyncMock())

        assert inner_app.call_count == 5

    async def test_blocks_at_threshold(self):
        """Запрос сверх лимита получает 429."""
        inner_app = AsyncMock()
        middleware = RateLimitMiddleware(inner_app, max_requests=3, window_seconds=60)
        scope = await _make_scope()

        # 3 запроса проходят
        for _ in range(3):
            await middleware(scope, AsyncMock(), AsyncMock())

        # 4-й — блокируется
        send = AsyncMock()
        await middleware(scope, AsyncMock(), send)

        # send вызван 2 раза: http.response.start + http.response.body
        assert send.call_count == 2
        start_call = send.call_args_list[0][0][0]
        assert start_call["status"] == 429

    @patch("app.middleware.time.time")
    async def test_window_expires(self, mock_time):
        """После истечения окна счётчик сбрасывается."""
        inner_app = AsyncMock()
        middleware = RateLimitMiddleware(inner_app, max_requests=2, window_seconds=60)
        scope = await _make_scope()

        # Два запроса в момент t=100
        mock_time.return_value = 100.0
        for _ in range(2):
            await middleware(scope, AsyncMock(), AsyncMock())

        # Прошло 61 секунда — окно истекло
        mock_time.return_value = 161.0
        await middleware(scope, AsyncMock(), AsyncMock())

        # Все 3 вызова прошли к inner_app (старые метки удалены)
        assert inner_app.call_count == 3

    async def test_per_ip_isolation(self):
        """Лимит считается отдельно для каждого IP."""
        inner_app = AsyncMock()
        middleware = RateLimitMiddleware(inner_app, max_requests=1, window_seconds=60)

        scope_a = await _make_scope("10.0.0.1")
        scope_b = await _make_scope("10.0.0.2")

        await middleware(scope_a, AsyncMock(), AsyncMock())
        await middleware(scope_b, AsyncMock(), AsyncMock())

        # Оба прошли, хотя лимит = 1 на IP
        assert inner_app.call_count == 2

    async def test_passes_non_http_scopes(self):
        """Lifespan и websocket пропускаются без проверки."""
        inner_app = AsyncMock()
        middleware = RateLimitMiddleware(inner_app, max_requests=0, window_seconds=60)

        scope = {"type": "lifespan"}
        await middleware(scope, AsyncMock(), AsyncMock())

        assert inner_app.call_count == 1
