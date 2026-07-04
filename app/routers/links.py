"""HTTP-роуты для работы со ссылками."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.link import LinkCreate, LinkResponse
from app.services import link as link_service

router = APIRouter()

# Зарезервированные пути — нельзя создать alias с таким именем,
# иначе он «перекроет» реальный роут API.
RESERVED_PATHS = {"api", "docs", "redoc", "openapi.json", "health", "links"}


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


@router.get("/links", response_model=list[LinkResponse])
async def get_all_links(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Получить все ссылки текущего пользователя."""
    links = await link_service.get_all_links(db, user_id=user.id)
    return [_to_response(link) for link in links]


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
