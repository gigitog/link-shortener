"""Юнит-тесты JSONFormatter: LogRecord -> валидная JSON-строка с нужными полями."""

import json
import logging

from app.logging_config import JSONFormatter, request_id_var


def _make_record(**extra) -> logging.LogRecord:
    """Собирает LogRecord так же, как это делает сам logging при logger.info(...)."""
    record = logging.LogRecord(
        name="link_shortener",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="%s %s -> %s",
        args=("GET", "/links", 200),
        exc_info=None,
    )
    for key, value in extra.items():
        setattr(record, key, value)
    return record


class TestJSONFormatter:
    def test_basic_fields(self):
        record = _make_record()
        payload = json.loads(JSONFormatter().format(record))

        assert payload["level"] == "INFO"
        assert payload["logger"] == "link_shortener"
        assert payload["message"] == "GET /links -> 200"
        assert "timestamp" in payload
        assert "request_id" not in payload

    def test_extra_http_fields(self):
        record = _make_record(method="GET", path="/links", status_code=200, duration_ms=1.23)
        payload = json.loads(JSONFormatter().format(record))

        assert payload["method"] == "GET"
        assert payload["path"] == "/links"
        assert payload["status_code"] == 200
        assert payload["duration_ms"] == 1.23

    def test_request_id_from_contextvar(self):
        token = request_id_var.set("abc-123")
        try:
            payload = json.loads(JSONFormatter().format(_make_record()))
        finally:
            request_id_var.reset(token)

        assert payload["request_id"] == "abc-123"

    def test_exception_formatted(self):
        try:
            raise ValueError("boom")
        except ValueError:
            import sys

            record = _make_record()
            record.exc_info = sys.exc_info()

        payload = json.loads(JSONFormatter().format(record))
        assert "ValueError: boom" in payload["exception"]

    def test_cyrillic_not_escaped(self):
        """ensure_ascii=False — кириллица в логе читаема, а не \\uXXXX."""
        record = logging.LogRecord(
            name="link_shortener",
            level=logging.WARNING,
            pathname=__file__,
            lineno=1,
            msg="ссылка не найдена",
            args=(),
            exc_info=None,
        )
        raw = JSONFormatter().format(record)
        assert "ссылка не найдена" in raw
