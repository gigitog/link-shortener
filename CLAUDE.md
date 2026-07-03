# CLAUDE.md

Инструкции для Claude Code при работе над этим проектом. Читается в начале каждой сессии.

## О проекте

Сокращатель ссылок (link shortener). **Пет-проект для подготовки к собеседованию.**
Главная цель — не сам сервис, а изучение технологий: Docker, Kubernetes, REST API,
авторизация, middleware.

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
- **Pydantic** — валидация схем запросов/ответов.
- **Ruff** — линтер и форматтер.

## Команды

```bash
uv sync                              # установить зависимости
uv add <пакет>                       # добавить зависимость в проект
uv run ruff check .                  # линтер
uv run ruff format .                 # форматтер
uv run uvicorn app.main:app --reload # запуск dev-сервера (http://localhost:8000/docs)
```

Локальный Postgres для разработки (без docker-compose, появится на этапе 4):

```bash
docker run -d --name link-shortener-db \
  -e POSTGRES_USER=app -e POSTGRES_PASSWORD=app -e POSTGRES_DB=link_shortener \
  -p 5434:5432 postgres:17
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
3. **Авторизация и middleware** — пользователи, JWT, middleware (логирование, rate-limit, auth). ← *сейчас здесь*
4. **Docker** — Dockerfile + docker-compose (app + Postgres).
5. **Деплой на Hetzner** — самый дешёвый VPS, запуск через docker-compose.
6. **Kubernetes** — перенос в k3s: манифесты, Ingress, Secrets, масштабирование.
   Сюда же — мультидоменность (несколько host в Ingress + автоматический TLS per-domain
   через cert-manager). Схема БД под это уже готова (колонка `domain` в `links`).

Важные решения по ходу проекта фиксируем в `DECISIONS.md`.
