"""ASGI-middleware: логирование запросов и rate limiting.

Middleware — это «обёртка» вокруг всего приложения. Каждый HTTP-запрос
проходит через middleware ДО того, как попадёт в роутер, и ответ тоже
проходит через middleware на обратном пути:

    Клиент → Middleware → Роутер → Сервис → БД
    Клиент ← Middleware ← Роутер ← Сервис ← БД

Это удобно для сквозных задач: логирование, замер времени, rate-limit,
CORS — всё, что нужно для КАЖДОГО запроса, а не для одного роута.
"""

import json
import logging
import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger("link_shortener")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Логирует каждый запрос: метод, путь, статус и время ответа."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start

        logger.info(
            "%s %s → %s (%.3fs)",
            request.method,
            request.url.path,
            response.status_code,
            duration,
        )

        return response


class RateLimitMiddleware:
    """In-memory rate limiter на основе алгоритма «sliding window log».

    Реализован как чистый ASGI-middleware (не BaseHTTPMiddleware),
    чтобы избежать проблем совместимости при нескольких BaseHTTPMiddleware в стеке.

    Для каждого IP храним список временных меток (timestamps) запросов.
    При новом запросе:
    1) Удаляем метки старше window_seconds
    2) Если оставшихся >= max_requests — отказываем (429)
    3) Иначе — добавляем текущую метку и пропускаем

    Ограничения:
    - Хранение в памяти процесса — не работает с несколькими инстансами
      (каждый считает отдельно). Для прода нужен Redis.
    - Память растёт с числом уникальных IP. Для MVP — достаточно.
    """

    def __init__(self, app: ASGIApp, max_requests: int = 30, window_seconds: int = 60):
        self.app = app
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # {ip: [timestamp, timestamp, ...]}
        self.requests: dict[str, list[float]] = defaultdict(list)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # ASGI обрабатывает не только HTTP — пропускаем lifespan и websocket
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # scope["client"] — кортеж (host, port) или None
        client = scope.get("client")
        client_ip = client[0] if client else "unknown"
        now = time.time()

        # Шаг 1: убираем устаревшие метки (старше window)
        timestamps = self.requests[client_ip]
        self.requests[client_ip] = [ts for ts in timestamps if now - ts < self.window_seconds]

        # Шаг 2: проверяем лимит
        if len(self.requests[client_ip]) >= self.max_requests:
            logger.warning("rate limit exceeded for %s", client_ip)
            # Формируем 429 ответ вручную через ASGI-протокол
            body = json.dumps({"detail": "слишком много запросов, попробуйте позже"}).encode()
            await send(
                {
                    "type": "http.response.start",
                    "status": 429,
                    "headers": [
                        [b"content-type", b"application/json"],
                        [b"content-length", str(len(body)).encode()],
                    ],
                }
            )
            await send({"type": "http.response.body", "body": body})
            return

        # Шаг 3: записываем текущий запрос и пропускаем дальше
        self.requests[client_ip].append(now)
        await self.app(scope, receive, send)
