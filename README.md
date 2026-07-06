# Link Shortener

Сервис сокращения ссылок. Пет-проект для изучения FastAPI, Docker и Kubernetes.

## Стек

- Python 3.13, [uv](https://docs.astral.sh/uv/)
- FastAPI + Uvicorn (async)
- PostgreSQL + SQLAlchemy 2.x (async) + Alembic
- JWT-авторизация (bcrypt + PyJWT)
- Ruff (линтер/форматтер)

## Архитектура

Слоистая структура: роутер (HTTP) → сервис (бизнес-логика) → модель (БД).

```mermaid
graph LR
    Client[Клиент] --> MW[Middleware<br/>logging + rate limit]
    MW --> Auth[Auth Router<br/>/auth/*]
    MW --> Links[Links Router<br/>/links/*, /code]
    Auth --> AS[Auth Service<br/>JWT, bcrypt]
    Auth --> US[User Service<br/>CRUD]
    Links --> LS[Link Service<br/>CRUD]
    US --> DB[(PostgreSQL)]
    LS --> DB
```

## Схема БД

```mermaid
erDiagram
    users {
        bigint id PK
        varchar email UK
        varchar hashed_password
        datetime created_at
    }
    links {
        bigint id PK
        varchar domain
        varchar short_code
        text original_url
        int clicks_count
        datetime created_at
        bigint user_id FK
    }
    users ||--o{ links : "владеет"
```

## Поток запроса

```mermaid
sequenceDiagram
    participant C as Клиент
    participant M as Middleware
    participant R as Router
    participant S as Service
    participant DB as PostgreSQL

    Note over C,DB: Создание ссылки (POST /links)
    C->>M: POST /links + JWT
    M->>M: rate limit ✓
    M->>R: запрос
    R->>R: Depends(get_current_user) → User
    R->>S: create_link(url, user_id)
    S->>DB: INSERT INTO links
    DB-->>S: Link
    S-->>R: Link
    R-->>C: 201 + LinkResponse

    Note over C,DB: Редирект (GET /{code})
    C->>M: GET /abc1234
    M->>R: запрос
    R->>S: get_link_by_code("abc1234")
    S->>DB: SELECT ... WHERE short_code=
    DB-->>S: Link
    S->>S: increment_clicks
    R-->>C: 307 → original_url
```

## Запуск

### Вариант A — весь стек в Docker (проще всего)

```bash
cp .env.example .env              # заполнить значения (как минимум SECRET_KEY)
docker compose up --build         # поднимет app + Postgres
# → http://localhost:8000/docs
```

Контейнер `app` сам применяет миграции (`alembic upgrade head`) при старте.
Данные БД лежат в named volume `pgdata` и переживают `docker compose down`.

### Вариант B — гибридный dev-режим (hot-reload)

БД поднимаем в Docker, приложение запускаем локально через uv — так работает
`--reload` и отладка в IDE:

```bash
uv sync
cp .env.example .env              # DATABASE_URL уже указывает на localhost:5434

docker compose up -d db           # только Postgres (порт 5434 наружу)
uv run alembic upgrade head       # миграции с хоста
uv run uvicorn app.main:app --reload
# → http://localhost:8000/docs
```

> SQL-логи в консоль включаются переменной `DB_ECHO=true` в `.env` (по умолчанию выключены).

## API

| Метод | Путь | Авторизация | Описание |
|-------|------|:-----------:|----------|
| `POST` | `/auth/register` | — | Регистрация |
| `POST` | `/auth/login` | — | Логин → JWT-токен |
| `GET` | `/auth/me` | 🔒 | Данные текущего пользователя |
| `POST` | `/links` | 🔒 | Создать короткую ссылку |
| `GET` | `/links` | 🔒 | Список своих ссылок |
| `GET` | `/links/{code}` | — | Информация о ссылке |
| `GET` | `/{code}` | — | Редирект → оригинальный URL |

## Тесты

```bash
# Поднять тестовую БД (отдельный контейнер, порт 5433, данные в RAM)
docker compose -f docker-compose.test.yml up -d

# Запуск тестов
uv run pytest -v

# С покрытием
uv run pytest --cov=app --cov-report=term-missing

# Только unit / только integration
uv run pytest tests/unit/ -v
uv run pytest tests/integration/ -v
```

75 тестов, покрытие 92%. Изоляция через SAVEPOINT + rollback (реальный Postgres, без моков БД).

## Docker

- `Dockerfile` — multi-stage (builder → runtime), non-root пользователь, кэширование
  слоя зависимостей. Финальный образ ~68 МБ (сжатый).
- `docker-compose.yml` — app + Postgres, связь по DNS-имени `db`, healthcheck, персистентный volume.
- `docker/entrypoint.sh` — миграции перед запуском сервера.
- `docker-compose.test.yml` — отдельная тестовая БД (данные в RAM, порт 5433).

## Статус

🚧 В разработке. Дорожная карта — в [CLAUDE.md](CLAUDE.md), ключевые решения — в [DECISIONS.md](DECISIONS.md).
