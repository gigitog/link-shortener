"""Health-эндпоинты для оркестраторов (Docker healthcheck, в будущем — K8s-пробы).

Два разных вопроса, две разные проверки:

- liveness (/health)       — «процесс жив, не завис»? Не трогает БД.
  Если падает — оркестратор ПЕРЕЗАПУСКАЕТ контейнер.
- readiness (/health/ready) — «готов обслуживать трафик»? Проверяет зависимости (БД).
  Если падает — оркестратор УБИРАЕТ из балансировки, но не перезапускает
  (проблема может быть на стороне БД, а не приложения — рестарт её не починит).

Смешивать их нельзя: если проверять БД в liveness, кратковременный лаг БД
приведёт к бессмысленным перезапускам полностью здорового приложения.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    """Liveness: приложение запущено и обрабатывает запросы."""
    return {"status": "ok"}


@router.get("/health/ready")
async def health_ready(db: AsyncSession = Depends(get_db)):
    """Readiness: приложение готово обслуживать трафик (БД отвечает)."""
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        raise HTTPException(status_code=503, detail="база данных недоступна") from e

    return {"status": "ok"}
