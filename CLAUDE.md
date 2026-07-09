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

Фронтенд (`frontend/`):

- **React 19 + Vite + TypeScript** — SPA, статика раздаётся отдельным nginx-контейнером.
- **Tailwind CSS v4** — стили (плагин в vite.config, без postcss-конфига).
- **TanStack Query** — серверное состояние (кэш, инвалидация) + нативный fetch (без axios).
- **react-router-dom v7** — роутинг.
- **react-i18next** — интерфейс на немецком (`de.json`), английский — поздний этап.
- **oxlint** — линтер.

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

Фронтенд (`frontend/`):

```bash
npm install       # установить зависимости
npm run dev        # dev-сервер Vite с HMR (http://localhost:5173, проксирует /api на :8000)
npm run lint        # oxlint
npm run build       # tsc -b && vite build → frontend/dist
```

Docker (этап 5, фронтенд — этап 8):

```bash
docker compose up --build     # весь стек: app + frontend + Postgres (миграции при старте app)
docker compose up -d db       # только БД (для гибридного dev-режима: app через uv, frontend через npm run dev)
docker compose down           # остановить (volume pgdata с данными остаётся)
docker compose logs -f app    # логи приложения
```

Прод (подробнее — `docs/deploy.md`):

```bash
# Деплой теперь автоматический: merge PR в main → workflow Deploy сам собирает
# образ, пушит в GHCR и обновляет сервер по SSH. Руками ничего не нужно.

# Ручной запасной путь (Actions недоступен). Сервер НЕ собирает образы — тянет из GHCR:
ssh deploy@178.105.29.149     # сервер Hetzner (вход только по SSH-ключу)
cd ~/link-shortener && git pull \
  && docker compose -f docker-compose.yml -f docker-compose.prod.yml pull app frontend \
  && docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

Сервис: https://s.faiuk.me (Caddy терминирует TLS, наружу открыты только 80/443).
Роутинг одним доменом: `/api/*` → `app`, страницы SPA → `frontend` (nginx), всё
остальное (короткие коды, `/docs`) → `app` — см. `docker/Caddyfile`.

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

## Структура frontend/src/

```
frontend/src/
  main.tsx            — QueryClientProvider, i18n init, RouterProvider
  router.tsx          — /, /login, /register, /dashboard, /about, /*(404)
  vite-env.d.ts        — типы env-переменных Vite (VITE_APP_VERSION)
  api/
    client.ts          — fetch-обёртка: BASE=/api, JWT из localStorage, ApiError, 401→logout
    auth.ts  links.ts  types.ts   — вызовы API + TS-зеркала Pydantic-схем
  auth/
    AuthContext.tsx     — token в state + localStorage; login()/logout()
    RequireAuth.tsx      — guard: нет токена → <Navigate to="/login">
  components/           — Layout, Header, Footer, Spinner, ErrorMessage,
                          LinkForm, LinkTable, Pagination, CopyButton
  pages/                — HomePage, LoginPage, RegisterPage, DashboardPage,
                          AboutPage, NotFoundPage
  i18n/index.ts de.json  — lng: 'de'; ключи по неймспейсам (nav.*, auth.*,
                          links.*, home.*, about.*, footer.*, errors.*)
  lib/
    errors.ts           — (status, контекст) → i18n-ключ немецкого сообщения
    validation.ts        — PASSWORD_MIN_LENGTH, ALIAS_RE, isValidUrl
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
   на push в main: сборка Docker-образа, пуш в registry (GHCR), автодеплой на Hetzner. ✅
   - В ci.yml — grep на деструктивные миграции (`drop_table`, `drop_column`): warning,
     но не блокирует (иногда DROP нужен). Мини-улучшение, можно добавить в любой момент.
7.1. **Бэкап БД** — `pg_dump` по cron на сервере (`docker/backup.sh`), хранение
   14 дней локально на диске хоста (вне docker volume `pgdata`). ✅
   Офсайт-копия в Object Storage осознанно отложена (платно, не оправдано
   для пет-проекта пока) — см. `docs/deploy.md` и `DECISIONS.md`.
8. **Фронтенд** — React + Vite + TypeScript, статика раздаётся отдельным nginx-контейнером,
   Caddy роутит по пути на одном домене. Немецкий интерфейс, страница «Über das Projekt»,
   пометка pet-project + версия в футере. Реализован на 5 PR (пагинация+CORS → каркас →
   dashboard → лендинг/About → cutover); подробности — `DECISIONS.md`. ✅
9. **Мониторинг / observability** — эндпоинты `/health` (liveness) и `/health/ready`
   (readiness), структурированные JSON-логи + `request_id`, метрики Prometheus
   (`prometheus-fastapi-instrumentator`) + Grafana в `docker-compose.observability.yml`
   (дашборд по RED-методу, доступ по SSH-туннелю — не публичный). ✅
10. **Кэш (Redis)** ← *сейчас здесь* — cache-aside для горячего пути `GET /{code}` (редирект без похода в БД);
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
17. **Публичный дашборд `/metrics-dashboard`** — обобщённые live-метрики для посетителей/
    рекрутёров (нагрузка, число запросов, задержки), без детализации по конкретным роутам —
    это не то же самое, что `/metrics` для Prometheus (тот закрыт снаружи, см. `docker/Caddyfile`).
    Обновление раз в 30–120 сек через polling (`TanStack Query` + `refetchInterval`), не
    WebSocket — для такого интервала живое соединение не нужно, а с несколькими репликами
    (этап 11) WebSocket потребовал бы липких сессий/pub-sub. Бэкенд-эндпоинт агрегирует
    `prometheus_client.REGISTRY` внутри процесса (тот же `generate_latest()`) и отдаёт
    только безопасный обобщённый срез.
18. **Кастомные короткие коды (vanity) или QR-коды** — либо пользователь сам вводит код
    (валидация + уникальность, обработка 409), либо эндпоинт отдаёт QR (PNG/SVG) + кнопка скачивания.
19. **Смена пароля** — `POST /auth/change-password` со старым паролем (переиспользуем bcrypt);
    форма в настройках. Дальше можно дорасти до сброса по email (новая инфраструктура — отправка писем).
20. **Mobile UI Adaptation** — адаптив фронта под мобильные экраны (responsive-вёрстка, тач-навигация).
21. **Локализация API / Swagger** — публичный `/docs` открыт рекрутерам, поэтому внешние тексты
    API переводим на **английский** (в приоритете): `summary`/`description` эндпоинтов, теги,
    сообщения в `detail` у HTTPException. Немецкий как второй язык — по возможности и позже
    (не критично). **Комментарии в коде остаются на русском** — это внутренняя кодовая база
    для автора, а не витрина. Сделать можно раньше по номеру, если руки дойдут — задача
    изолированная (правки строк, без миграций и логики).

Важные решения по ходу проекта фиксируем в `DECISIONS.md`.
