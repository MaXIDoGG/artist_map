#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

COMPOSE="docker compose -f docker-compose.prod.yml"

if [[ ! -f .env ]]; then
  echo "Создайте .env из .env.production.example"
  exit 1
fi

if [[ "${RESTORE_DB:-}" == "1" ]]; then
  echo "==> Сброс тома PostgreSQL перед восстановлением"
  $COMPOSE down -v 2>/dev/null || true
fi

echo "==> Сборка образов"
$COMPOSE build

echo "==> Запуск PostgreSQL"
$COMPOSE up -d postgres

echo "==> Ожидание PostgreSQL"
until $COMPOSE exec -T postgres pg_isready -U artist_map -d artist_map >/dev/null 2>&1; do
  sleep 2
done

if [[ "${RESTORE_DB:-}" == "1" && -f backups/artist_map.sql ]]; then
  echo "==> Восстановление базы из backups/artist_map.sql"
  $COMPOSE exec -T postgres psql -U artist_map -d artist_map -v ON_ERROR_STOP=1 < backups/artist_map.sql
fi

echo "==> Запуск всех сервисов"
$COMPOSE up -d

echo "==> Статус"
$COMPOSE ps

echo "Готово. Проверка: curl -s http://127.0.0.1/api/v1/health"
