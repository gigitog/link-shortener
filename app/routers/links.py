"""HTTP-роуты для работы со ссылками."""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.link import LinkCreate, LinkListResponse, LinkResponse
from app.services import link as link_service

router = APIRouter()

# Зарезервированные пути — нельзя создать alias с таким именем,
# иначе он «перекроет» реальный роут API или страницу фронтенда:
# в проде Caddy отдаёт пути SPA (login, dashboard, ...) контейнеру фронта,
# и короткая ссылка с таким кодом стала бы недостижимой.
RESERVED_PATHS = {
    "api",
    "auth",
    "docs",
    "redoc",
    "openapi.json",
    "health",
    "metrics",
    "links",
    # страницы SPA + папка статики Vite (см. docker/Caddyfile, матчер @spa)
    "login",
    "register",
    "dashboard",
    "about",
    "assets",
}


def _build_short_url(short_code: str) -> str:
    """Собирает полный короткий URL из BASE_URL и кода."""
    return f"{settings.base_url.rstrip('/')}/{short_code}"


def _to_response(link) -> LinkResponse:
    """Собирает LinkResponse из ORM-объекта Link. Общая точка для всех роутов."""
    return LinkResponse(
        id=link.id,
        short_code=link.short_code,
        original_url=link.original_url,
        short_url=_build_short_url(link.short_code),
        clicks_count=link.clicks_count,
        created_at=link.created_at,
    )


@router.post("/links", response_model=LinkResponse, status_code=201)
async def create_link(
    body: LinkCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Создать короткую ссылку (требует авторизации)."""
    if body.custom_alias and body.custom_alias.lower() in RESERVED_PATHS:
        raise HTTPException(
            status_code=400,
            detail=f"'{body.custom_alias}' — зарезервированное имя",
        )

    try:
        link = await link_service.create_link(
            db,
            str(body.original_url),
            body.custom_alias,
            user_id=user.id,
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from None

    return _to_response(link)


@router.get("/links", response_model=LinkListResponse)
async def get_links(
    # Query(...) с ge/le — валидация прямо в сигнатуре: limit=0 или limit=101 → 422.
    # Потолок 100 защищает БД от запроса «отдай всё» одним махом.
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Получить страницу ссылок текущего пользователя (новые сверху)."""
    links, total = await link_service.get_links_page(
        db, user_id=user.id, limit=limit, offset=offset
    )
    return LinkListResponse(
        items=[_to_response(link) for link in links],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/links/{short_code}", response_model=LinkResponse)
async def get_link_info(short_code: str, db: AsyncSession = Depends(get_db)):
    """Получить информацию о ссылке (без редиректа)."""
    link = await link_service.get_link_by_code(db, short_code)
    if not link:
        raise HTTPException(status_code=404, detail="ссылка не найдена")

    return _to_response(link)


@router.get("/{short_code}")
async def redirect_to_original(short_code: str, db: AsyncSession = Depends(get_db)):
    """
    Главный роут сокращателя: GET /{code} → 307 редирект на оригинальный URL.

    307 (а не 301), чтобы браузер не кешировал редирект навсегда —
    иначе счётчик кликов перестанет считаться.
    """
    link = await link_service.get_link_by_code(db, short_code)
    if not link:
        raise HTTPException(status_code=404, detail="ссылка не найдена")

    await link_service.increment_clicks(db, link.id)
    return RedirectResponse(url=link.original_url, status_code=307)
