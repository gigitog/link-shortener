#!/usr/bin/env bash
# Бэкап БД на проде: pg_dump из контейнера db -> сжатый файл на диске хоста.
# Запускается по cron на сервере (см. docs/deploy.md).
#
# Почему pg_dump, а не снимок volume pgdata: dump — консистентная логическая
# копия (транзакционный snapshot), не зависит от файлового формата Postgres
# и восстанавливается даже на другой версии/машине. Снимок volume пришлось бы
# делать при остановленной БД, иначе есть риск словить файлы в промежуточном
# состоянии.
#
# Почему каталог с бэкапами вне docker volume pgdata: если том с самой БД
# случайно снесут (docker volume rm, ошибка при пересоздании), копии не должны
# уехать вместе с ним.

set -euo pipefail

BACKUP_DIR="$HOME/backups"
KEEP_DAYS=14
STAMP="$(date +%F_%H%M%S)"
FILE="$BACKUP_DIR/link_shortener_$STAMP.sql.gz"

mkdir -p "$BACKUP_DIR"
cd "$(dirname "$0")/.."

# pg_dump выполняется ВНУТРИ контейнера db — там уже есть переменные
# POSTGRES_USER/POSTGRES_DB (заданы в environment сервиса), поэтому скрипту
# не нужно самому парсить .env.
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T db \
  sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' | gzip > "$FILE"

# Ротация: удаляем локальные копии старше KEEP_DAYS дней.
find "$BACKUP_DIR" -name 'link_shortener_*.sql.gz' -mtime "+$KEEP_DAYS" -delete

echo "$(date -Iseconds) backup ok: $FILE ($(du -h "$FILE" | cut -f1))"
