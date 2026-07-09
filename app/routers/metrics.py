"""Эндпоинт /metrics — отдаёт снимок метрик в текстовом формате Prometheus.

Prometheus сам ходит сюда по расписанию (scrape) — см. app/metrics.py про
pull-модель. Никакой аутентификации не требуется (как и для /health):
метрики тоже "инфраструктурный" эндпоинт, не бизнес-данные.
"""

from fastapi import APIRouter
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import Response

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
async def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
