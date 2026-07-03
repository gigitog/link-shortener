# Link Shortener

Сервис сокращения ссылок. Пет-проект для изучения FastAPI, Docker и Kubernetes.

## Стек

- Python 3.13, [uv](https://docs.astral.sh/uv/)
- FastAPI + Uvicorn
- PostgreSQL + SQLAlchemy (async)
- Ruff (линтер/форматтер)

## Запуск (локально)

```bash
uv sync                 # установить зависимости
cp .env.example .env    # создать конфиг и заполнить значения
# запуск сервера появится на этапе разработки API
```

## Статус

🚧 В разработке. Дорожная карта — в [CLAUDE.md](CLAUDE.md), ключевые решения — в [DECISIONS.md](DECISIONS.md).
