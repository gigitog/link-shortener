# Прод-сервер: шпаргалка

Сервис живёт на https://s.faiuk.me (Hetzner Cloud CX22, Ubuntu 24.04, Falkenstein).

## Доступ

```bash
ssh deploy@178.105.29.149   # вход только по SSH-ключу, пароли выключены
```

Пользователь `deploy` (sudo + группа docker). Root — тоже только по ключу.
Firewall Hetzner Cloud: открыты только 22, 80, 443.

## Стек

`~/link-shortener` — клон GitHub-репозитория. Три контейнера:

- `caddy` — reverse proxy, TLS (сертификаты в volume `caddy_data` — не удалять!);
- `app` — FastAPI (порт 8000 только внутри docker-сети);
- `db` — Postgres 17 (данные в volume `pgdata` — не удалять!).

Все команды compose на проде — с двумя `-f`:

```bash
alias dcp='docker compose -f docker-compose.yml -f docker-compose.prod.yml'
```

## Обновить приложение (деплой новой версии)

**Обычный путь — автоматический.** Merge PR в `main` запускает workflow
`Deploy` (`.github/workflows/deploy.yml`): тесты → сборка образа → пуш в GHCR
→ SSH на сервер и обновление. Руками ничего делать не нужно, прогресс виден
на вкладке Actions. Кнопка «передеплоить без коммита» — там же (Run workflow).

**Ручной запасной путь** (если Actions недоступен). Сервер больше НЕ собирает
образ, а тянет готовый из GHCR — поэтому без `--build`:

```bash
cd ~/link-shortener
git pull
docker compose -f docker-compose.yml -f docker-compose.prod.yml pull app
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

Миграции применяются автоматически в entrypoint.

**Откат на прошлую версию.** У каждого образа есть тег с SHA коммита. Взять
конкретный образ вместо `latest`:

```bash
docker pull ghcr.io/gigitog/link-shortener:<SHA>
docker tag ghcr.io/gigitog/link-shortener:<SHA> ghcr.io/gigitog/link-shortener:latest
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Посмотреть, что происходит

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps          # статусы
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f app # логи приложения
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs caddy  # логи прокси/TLS
```

## Перезапуск / остановка

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml restart app  # только app
docker compose -f docker-compose.yml -f docker-compose.prod.yml down         # весь стек (volumes остаются)
sudo reboot  # стек поднимется сам (restart: unless-stopped)
```

## Секреты

`~/link-shortener/.env` — существует только на сервере, в git не попадает.
Переменные: POSTGRES_USER / POSTGRES_PASSWORD / POSTGRES_DB, SECRET_KEY,
DOMAIN, BASE_URL. Без любой из них стек не поднимется (`${VAR:?}` в compose).

## Чего пока нет (осознанно)

- Бэкапов БД — данные живут только в volume `pgdata`. TODO: pg_dump по cron.
- Мониторинга — только docker logs (появится на этапе 9).
