"""Интеграционные тесты LoggingMiddleware: request_id в заголовке и в логах."""

import json
import logging
import uuid

from httpx import AsyncClient

from app.logging_config import JSONFormatter, request_id_var


class _CaptureHandler(logging.Handler):
    """Форматирует запись СРАЗУ через JSONFormatter — как это делает реальный
    StreamHandler в проде (logging синхронный: formatter вызывается внутри
    logger.info(), пока request_id ещё лежит в contextvar).

    caplog так не умеет: он копит сырые LogRecord и форматирует их (если
    вообще форматирует) уже после теста, когда contextvar сброшен —
    для проверки JSON-вывода нужен именно «живой» хендлер.
    """

    def __init__(self):
        super().__init__()
        self.lines: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.lines.append(JSONFormatter().format(record))


class TestRequestId:
    async def test_header_is_valid_uuid4(self, client: AsyncClient):
        resp = await client.get("/openapi.json")
        request_id = resp.headers["x-request-id"]

        # Бросит ValueError, если это не валидный UUID
        uuid.UUID(request_id, version=4)

    async def test_different_per_request(self, client: AsyncClient):
        first = (await client.get("/openapi.json")).headers["x-request-id"]
        second = (await client.get("/openapi.json")).headers["x-request-id"]

        assert first != second

    async def test_contextvar_reset_after_request(self, client: AsyncClient):
        """После обработки запроса contextvar не должен «утекать» наружу."""
        assert request_id_var.get() is None
        await client.get("/openapi.json")
        assert request_id_var.get() is None

    async def test_log_line_has_request_id_and_http_fields(self, client: AsyncClient):
        logger = logging.getLogger("link_shortener")
        handler = _CaptureHandler()
        logger.addHandler(handler)
        try:
            resp = await client.get("/openapi.json")
        finally:
            logger.removeHandler(handler)

        request_id = resp.headers["x-request-id"]
        matching = [json.loads(line) for line in handler.lines if request_id in line]
        assert matching, "лог запроса не найден или не содержит совпадающий request_id"

        payload = matching[0]
        assert payload["request_id"] == request_id
        assert payload["method"] == "GET"
        assert payload["path"] == "/openapi.json"
        assert payload["status_code"] == 200
        assert "duration_ms" in payload
