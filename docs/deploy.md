# Прод-сервер: шпаргалка

Сервис живёт на https://s.faiuk.me (Hetzner Cloud CX22, Ubuntu 24.04, Falkenstein).

## Доступ

```bash
ssh deploy@178.105.29.149   # вход только по SSH-ключу, пароли выключены
```

Пользователь `deploy` (sudo + группа docker). Root — тоже только по ключу.
Firewall Hetzner Cloud: открыты только 22, 80, 443.

## Стек

`~/link-shortener` — клон GitHub-репозитория, зачекаученный на ветку **`main`**
(это ствол проекта — туда мержатся все PR, оттуда идёт автодеплой). Три контейнера:

- `caddy` — reverse proxy, TLS (сертификаты в volume `caddy_data` — не удалять!);
- `app` — FastAPI (порт 8000 только внутри docker-сети);
- `db` — Postgres 17 (данные в volume `pgdata` — не удалять!).

> ⚠️ **Сервер должен стоять на `main`.** Автодеплой делает `git pull` той ветки,
> на которой стоит сервер, — если он окажется на другой ветке (напр. старой
> `feature/deploy`), хостовые файлы (compose, Caddyfile, скрипты) на сервер
> приезжать перестанут, хотя образ `app` продолжит обновляться из GHCR
> (он идёт отдельным каналом). Проверить: `git branch --show-current` → `main`.

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

## Бэкапы БД

`docker/backup.sh` (приезжает на сервер вместе с `git pull`) раз в сутки по cron
делает `pg_dump` из контейнера `db`, сжимает и кладёт в `~/backups/` на диске
хоста — **не** в docker volume `pgdata`, чтобы копии не пропали вместе с ним
при случайной пересборке/удалении тома. Хранятся 14 дней (старее — удаляются
скриптом автоматически).

**Осознанно оставлено локально, без офсайт-копии** (Hetzner Object Storage —
платный, ~€4.90/мес, для пет-проекта пока не оправдано). Это защищает от
плохой миграции/случайного `DELETE`, но НЕ защищает от потери самого сервера
или диска целиком. Если проект вырастет — следующий шаг: rclone + бесплатный
S3-совместимый бакет (Backblaze B2 / Cloudflare R2).

Настройка cron на сервере (один раз):

```bash
chmod +x ~/link-shortener/docker/backup.sh
crontab -e
# добавить строку — каждый день в 03:00 по времени сервера:
0 3 * * * /home/deploy/link-shortener/docker/backup.sh >> /home/deploy/backups/backup.log 2>&1
```

Проверить, что бэкапы создаются:

```bash
ls -lh ~/backups
tail ~/backups/backup.log
```

**Восстановление из бэкапа** (например, после неудачной миграции):

```bash
cd ~/link-shortener
gunzip -c ~/backups/link_shortener_<STAMP>.sql.gz | \
  docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T db \
  sh -c 'psql -U "$POSTGRES_USER" "$POSTGRES_DB"'
```

⚠️ Это накатывает дамп поверх текущей БД (INSERT'ы упадут на конфликтах, если
данные уже есть) — перед восстановлением на «живую» БД сначала пересоздать
таблицы (`docker compose ... down -v` для `db`, поднять заново, накатить
дамп) либо восстанавливать в чистую БД для проверки.

## Чего пока нет (осознанно)

- Офсайт-копии бэкапов (см. выше) — только локально на сервере.
- Мониторинга — только docker logs (появится на этапе 9).
