"""Бизнес-логика работы со ссылками."""

import secrets
import string
from urllib.parse import urlparse

from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.link import Link

# Алфавит для генерации случайных кодов (base62: a-z + A-Z + 0-9 = 62 символа).
# 7 символов из 62 → 62^7 ≈ 3.5 триллиона комбинаций — коллизии крайне редки.
ALPHABET = string.ascii_letters + string.digits


def _generate_short_code() -> str:
    """Генерирует случайную строку из ALPHABET заданной длины."""
    return "".join(secrets.choice(ALPHABET) for _ in range(settings.short_code_length))


def _extract_domain() -> str:
    """Извлекает домен (host) из BASE_URL. Напр. 'http://localhost:8000' → 'localhost:8000'."""
    return urlparse(settings.base_url).netloc


async def create_link(
    db: AsyncSession,
    original_url: str,
    custom_alias: str | None = None,
    user_id: int | None = None,
) -> Link:
    """
    Создаёт короткую ссылку.

    Если custom_alias передан — использует его как short_code.
    Если нет — генерирует случайный и при коллизии пробует снова (до 5 попыток).

    user_id — ID владельца ссылки (из JWT-токена). Может быть None,
    если в будущем понадобятся анонимные ссылки.

    Возвращает созданный объект Link.
    Бросает ValueError, если custom_alias уже занят.
    """
    domain = _extract_domain()

    if custom_alias:
        link = Link(
            domain=domain,
            short_code=custom_alias,
            original_url=str(original_url),
            user_id=user_id,
        )
        db.add(link)
        try:
            await db.commit()
            await db.refresh(link)
            return link
        except IntegrityError:
            await db.rollback()
            raise ValueError(f"alias '{custom_alias}' уже занят") from None

    # Генерация случайного кода с retry на (маловероятную) коллизию
    max_attempts = 5
    for _ in range(max_attempts):
        code = _generate_short_code()
        link = Link(
            domain=domain,
            short_code=code,
            original_url=str(original_url),
            user_id=user_id,
        )
        db.add(link)
        try:
            await db.commit()
            await db.refresh(link)
            return link
        except IntegrityError:
            await db.rollback()

    raise RuntimeError("не удалось сгенерировать уникальный код после нескольких попыток")


async def get_link_by_code(db: AsyncSession, short_code: str) -> Link | None:
    """Находит ссылку по short_code (для текущего домена)."""
    domain = _extract_domain()
    result = await db.execute(
        select(Link).where(Link.domain == domain, Link.short_code == short_code)
    )
    return result.scalar_one_or_none()


async def get_links_page(
    db: AsyncSession,
    user_id: int,
    limit: int,
    offset: int,
) -> tuple[list[Link], int]:
    """
    Возвращает страницу ссылок пользователя + общее число его ссылок.

    Стабильный ORDER BY обязателен: без него Postgres не гарантирует порядок
    строк, и offset-пагинация может показать одну ссылку дважды, а другую
    пропустить. Сортируем «новые сверху»; id — tie-breaker на случай
    одинаковых created_at (id уникален, поэтому порядок полностью детерминирован).
    """
    domain = _extract_domain()
    where = (Link.domain == domain, Link.user_id == user_id)

    # Два запроса: COUNT по тем же условиям и сама страница.
    total = await db.scalar(select(func.count()).select_from(Link).where(*where))
    result = await db.execute(
        select(Link)
        .where(*where)
        .order_by(Link.created_at.desc(), Link.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all(), total


async def increment_clicks(db: AsyncSession, link_id: int) -> None:
    """Атомарно увеличивает счётчик кликов на 1."""
    await db.execute(
        update(Link).where(Link.id == link_id).values(clicks_count=Link.clicks_count + 1)
    )
    await db.commit()
