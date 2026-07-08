"""Настройка структурированного (JSON) логирования.

Зачем JSON, а не привычная строка вида "GET /links -> 200 (0.005s)":
человеку такая строка читаема, а агрегатору логов (Loki, ELK, CloudWatch) —
нет. Чтобы искать «все запросы с 5xx за последний час» или «все логи
конкретного request_id», логи должны быть структурными данными, а не текстом.

request_id_var — contextvars.ContextVar, а не обычная переменная или
аргумент функции. Это позволяет:
1) сгенерировать id один раз в middleware, на входе запроса;
2) прочитать его в JSONFormatter при выводе ЛЮБОГО лога, даже если он
   возник глубоко в сервисном слое, который ничего не знает про HTTP-запрос
   и request_id ему явно не передавали.

contextvars (а не threading.local) — потому что приложение асинхронное:
на один OS-поток может приходиться много параллельных запросов (задач
asyncio), и обычный threading.local их бы не различил.
"""

import contextvars
import json
import logging
from datetime import UTC, datetime

request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id", default=None
)

# Поля, которые middleware кладёт в LogRecord через logger.info(..., extra={...}).
# Если они есть у конкретной записи — добавляем в JSON, если нет — просто пропускаем.
_EXTRA_FIELDS = ("method", "path", "status_code", "duration_ms")


class JSONFormatter(logging.Formatter):
    """Форматирует каждую запись лога в одну JSON-строку."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        request_id = request_id_var.get()
        if request_id is not None:
            payload["request_id"] = request_id

        for field in _EXTRA_FIELDS:
            if hasattr(record, field):
                payload[field] = getattr(record, field)

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        # ensure_ascii=False — иначе кириллица (сообщения исключений) уйдёт
        # в лог как \uXXXX-escape-последовательности, нечитаемо для человека.
        return json.dumps(payload, ensure_ascii=False)


def setup_logging(level: int = logging.INFO) -> None:
    """Настраивает корневой логгер на JSON-вывод в stdout.

    Заменяет handlers целиком (а не добавляет через addHandler), чтобы
    повторный вызов (например, при переимпорте модуля в тестах) не привёл
    к дублированию хендлеров и, как следствие, к задвоенным строкам лога.
    """
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers = [handler]
