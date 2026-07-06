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

Прод (этап 6, подробнее — `docs/deploy.md`):

```bash
ssh deploy@178.105.29.149     # сервер Hetzner (вход только по SSH-ключу)
# на сервере, в ~/link-shortener — деплой новой версии:
git pull && docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

Сервис: https://s.faiuk.me (Caddy терминирует TLS, наружу открыты только 80/443).

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
6. **Деплой на Hetzner** — CX22, docker-compose + Caddy (авто-TLS), https://s.faiuk.me. ✅
7. **CI/CD (GitHub Actions)** — на PR: линтер (ruff) + тесты (pytest на реальном Postgres в CI);
   на push в main: сборка Docker-образа, пуш в registry (GHCR), автодеплой на Hetzner. ← *сейчас здесь*
8. **Фронтенд** — сначала план и дизайн, затем вайбкодинг. Стек: React + Vite + TypeScript,
   статика раздаётся отдельным nginx-контейнером. На бэкенде появляется CORS + минимальные
   доработки API под UI (пагинация списка ссылок). Реализуем на текущем API.
9. **Мониторинг / observability** — Prometheus (метрики) + Grafana (дашборды),
   эндпоинты `/health` (liveness) и `/metrics`, структурированные JSON-логи.
10. **Кэш (Redis)** — cache-aside для горячего пути `GET /{code}` (редирект без похода в БД);
    перенос состояния rate-limiter из памяти процесса в Redis (общий счётчик — готовит почву
    к нескольким репликам на этапе K8s).
11. **Kubernetes** — перенос в k3s: манифесты, Ingress, Secrets, масштабирование.
    Сюда же — мультидоменность (несколько host в Ingress + автоматический TLS per-domain
    через cert-manager). Схема БД под это уже готова (колонка `domain` в `links`).

### Фичи (этапы 12+)

Инфраструктура готова — дальше идёт поток фич, каждая проходит полный цикл как в реальных
проектах: ветка → PR → CI (линт + тесты) → merge → CD (автодеплой). Правило: каждая фича
приносит свои тесты. Многие фичи — вертикальный срез миграция БД → API → фронт.

12. **Срок жизни ссылки** — колонка `expires_at` (миграция); при редиректе проверка «протухла ли»
    (410 Gone); на фронте date-picker и бейдж «истекает через N дней».
13. **Редактирование и удаление ссылок** — `PATCH`/`DELETE` + soft-delete (`deleted_at`);
    на фронте кнопки «изменить/удалить», модалка, подтверждение.
14. **Редизайн UI / тёмная тема** — чисто фронтовая итерация (независимый деплой контейнера фронта).
15. **Аналитика кликов** — таблица `clicks` (timestamp, referrer, user-agent, страна по GeoIP);
    эндпоинт статистики; графики на фронте. Стыкуется с мониторингом (этап 9).
16. **Профиль пользователя** — расширение таблицы `users` (`display_name`, `timezone`, `avatar_url`);
    `PATCH /auth/me`; страница настроек на фронте.
17. **Кастомные короткие коды (vanity) или QR-коды** — либо пользователь сам вводит код
    (валидация + уникальность, обработка 409), либо эндпоинт отдаёт QR (PNG/SVG) + кнопка скачивания.
18. **Смена пароля** — `POST /auth/change-password` со старым паролем (переиспользуем bcrypt);
    форма в настройках. Дальше можно дорасти до сброса по email (новая инфраструктура — отправка писем).
19. **Mobile UI Adaptation** — адаптив фронта под мобильные экраны (responsive-вёрстка, тач-навигация).

Важные решения по ходу проекта фиксируем в `DECISIONS.md`.
