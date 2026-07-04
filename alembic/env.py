"""Конфигурация Alembic для async-миграций.

Alembic — инструмент для «миграций» базы данных. Миграция — это скрипт,
который меняет структуру БД (добавляет таблицу, колонку и т.д.)
и умеет откатить изменение назад. Это как git, но для схемы БД.

Этот файл говорит Alembic:
1) откуда брать URL подключения к Postgres (из нашего app/config.py)
2) какие модели сравнивать со схемой БД (Base.metadata)
"""

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Импортируем наши модели и настройки
from app.config import settings
from app.database import Base

# Импортируем все модели, чтобы Alembic «видел» их через Base.metadata.
# Без этого autogenerate не обнаружит таблицы.
from app.models import Link, User  # noqa: F401

config = context.config

# Подставляем DATABASE_URL из .env (через pydantic-settings),
# чтобы не дублировать его в alembic.ini.
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Alembic сравнивает эту metadata с реальной схемой БД
# и генерирует миграции автоматически (autogenerate).
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Offline-режим: генерирует SQL без подключения к БД."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Online-режим: подключается к БД и применяет миграции."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
