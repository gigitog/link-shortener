# CLAUDE.md

Инструкции для Claude Code при работе над этим проектом. Читается в начале каждой сессии.

## О проекте

Сокращатель ссылок (link shortener). **Пет-проект для подготовки к собеседованию.**
Главная цель — не сам сервис, а изучение технологий: Docker, Kubernetes, REST API,
авторизация, middleware, тестирование.

## Уровень автора и стиль общения

- Автор — **начинающий** разработчик. Объясняй нетривиальные решения: *почему* так, а не только *как*.
- Не вываливай сразу весь код — двигаемся **поэтапно**, обсуждая каждый шаг.
- Комментарии в коде на русском, поясняющие суть (не очевидное вроде `# цикл по списку`).
- Отвечай на русском.

## Стек

- **Python 3.13**, менеджер зависимостей — **uv** (не pip/poetry).
- **FastAPI** + Uvicorn — веб-фреймворк (async).
- **PostgreSQL** — БД с первого дня (не SQLite), т.к. дальше Docker/K8s.
- **SQLAlchemy 2.x (async)** — ORM.
- **Alembic (async)** — миграции БД.
- **Pydantic** — валидация схем запросов/ответов.
- **bcrypt** — хэширование паролей.
- **PyJWT** — создание/проверка JWT-токенов.
- **Ruff** — линтер и форматтер.
- **pytest** + pytest-asyncio + httpx — тестирование (async, реальный Postgres).
- **pytest-cov** — покрытие кода.

## Команды

```bash
uv sync                              # установить зависимости
uv sync --group test                 # + тестовые зависимости
uv add <пакет>                       # добавить зависимость в проект
uv run ruff check .                  # линтер
uv run ruff format .                 # форматтер
uv run uvicorn app.main:app --reload # запуск dev-сервера (http://localhost:8000/docs)
uv run alembic upgrade head          # применить миграции БД
uv run alembic revision --autogenerate -m "описание"  # создать новую миграцию

# Тесты
docker compose -f docker-compose.test.yml up -d  # поднять тестовую БД (порт 5433)
uv run pytest -v                                 # запуск тестов
uv run pytest --cov=app --cov-report=term-missing  # с покрытием
uv run pytest tests/unit/ -v                     # только unit-тесты
uv run pytest tests/integration/ -v              # только интеграционные
```

Docker (этап 5):

```bash
docker compose up --build     # весь стек: app + Postgres (миграции при старте app)
docker compose up -d db       # только БД (для гибридного dev-режима: app через uv)
docker compose down           # остановить (volume pgdata с данными остаётся)
docker compose logs -f app    # логи приложения
```

## Структура app/

```
app/
  config.py           — настройки из .env (pydantic-settings)
  database.py         — async engine, sessionmaker, Base, get_db
  dependencies.py     — get_current_user (JWT → User)
  main.py             — FastAPI app, middleware, роутеры
  middleware.py        — LoggingMiddleware, RateLimitMiddleware
  models/
    link.py           — таблица links (FK → users)
    user.py           — таблица users
  routers/
    auth.py           — POST /auth/register, POST /auth/login, GET /auth/me
    links.py          — POST /links, GET /links, GET /links/{code}, GET /{code}
  schemas/
    link.py           — LinkCreate, LinkResponse
    user.py           — UserCreate, UserResponse, Token
  services/
    auth.py           — hash_password, verify_password, create/decode JWT
    link.py           — CRUD ссылок
    user.py           — регистрация, аутентификация
```

## Конвенции

- Секреты и конфиг — только через переменные окружения (`.env`, в git не коммитим).
  В репозитории лежит `.env.example` как шаблон.
- Структура `app/`: `routers/` (тонкий HTTP-слой) → `services/` (бизнес-логика) →
  `models/` (SQLAlchemy) + `schemas/` (Pydantic). Роутер не должен знать деталей БД.
- Ветки: `feature/*` для новых кусков; коммиты в стиле Conventional Commits
  (`feat:`, `fix:`, `chore:`, `docs:`).

## Дорожная карта (этапы)

1. **Фундамент** — git, конфиги, CLAUDE.md, DECISIONS.md. ✅
2. **MVP API** — роуты создания/редиректа ссылок + Postgres, локально без Docker. ✅
3. **Авторизация и middleware** — пользователи, JWT, Alembic, middleware (логирование, rate-limit). ✅
4. **Тестирование** — pytest, тесты для API и сервисов. ✅
5. **Docker** — Dockerfile + docker-compose (app + Postgres). ✅
6. **Деплой на Hetzner** — самый дешёвый VPS, запуск через docker-compose. ← *сейчас здесь*
7. **Kubernetes** — перенос в k3s: манифесты, Ingress, Secrets, масштабирование.
   Сюда же — мультидоменность (несколько host в Ingress + автоматический TLS per-domain
   через cert-manager). Схема БД под это уже готова (колонка `domain` в `links`).

Важные решения по ходу проекта фиксируем в `DECISIONS.md`.
