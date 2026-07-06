# Dockerfile v2 — production-grade: multi-stage build, кэширование слоёв, non-root.
#
# Идея multi-stage: сборка идёт в два «этажа» (stage).
#   1) builder — здесь есть uv, здесь ставятся зависимости в .venv
#   2) runtime — сюда КОПИРУЕМ только готовый .venv и код, а uv и кэши выбрасываем
# В финальный образ попадает лишь второй этаж → он меньше и в нём нет лишних
# инструментов (меньше поверхность атаки).

# ---------- Stage 1: builder ----------
FROM python:3.13-slim AS builder

# uv копируем из официального образа Astral. Версия запинена = локальной.
COPY --from=ghcr.io/astral-sh/uv:0.11.6 /uv /uvx /bin/

# Настройки uv для сборки в контейнере:
# UV_COMPILE_BYTECODE=1  — заранее скомпилировать .pyc (чуть быстрее старт приложения)
# UV_LINK_MODE=copy      — копировать файлы в .venv, а не делать hardlink
#                          (hardlink между кэшем и .venv в Docker часто невозможен)
# UV_PYTHON_DOWNLOADS=0  — не качать свой Python, использовать системный из образа
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# --- Ключевой приём: кэширование слоя с зависимостями ---
# Сначала копируем ТОЛЬКО манифесты зависимостей (pyproject.toml + uv.lock),
# без кода приложения. Слой RUN uv sync зависит только от этих двух файлов,
# поэтому Docker пересоберёт его лишь при смене зависимостей.
# Правка кода в app/ этот тяжёлый слой НЕ инвалидирует.
COPY pyproject.toml uv.lock ./

# --mount=type=cache — кэш скачанных пакетов uv переживает пересборки образа
# (он хранится на хосте BuildKit, а не в слоях образа).
# --no-install-project — ставим только зависимости, но не сам проект как пакет.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Теперь копируем исходники и доустанавливаем сам проект.
# Этот слой пересобирается при любой правке кода — но он дешёвый,
# т.к. все внешние зависимости уже лежат в .venv из предыдущего слоя.
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ---------- Stage 2: runtime ----------
# Финальный образ: чистый python-slim без uv, без кэшей, без dev-инструментов.
FROM python:3.13-slim AS runtime

# PYTHONUNBUFFERED=1 — stdout/stderr не буферизуются, логи видны в docker logs сразу.
# PATH — чтобы python/uvicorn брались из нашего .venv без активации окружения.
ENV PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Создаём непривилегированного пользователя.
# Зачем: по умолчанию процесс в контейнере работает от root. Если в приложении
# найдут дыру и «выберутся» из процесса — получат root внутри контейнера.
# Обычный пользователь снижает ущерб. Это стандартное требование безопасности.
RUN groupadd --system app && useradd --system --gid app --home-dir /app app

WORKDIR /app

# Копируем из builder-стадии готовое окружение и код.
# --chown=app:app — сразу назначаем владельцем нашего пользователя.
COPY --from=builder --chown=app:app /app /app

# Переключаемся на непривилегированного пользователя.
# Все последующие процессы (в т.ч. CMD) идут от него.
USER app

EXPOSE 8000

# .venv уже в PATH, поэтому зовём uvicorn напрямую, без `uv run`.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
