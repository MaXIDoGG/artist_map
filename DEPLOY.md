# Деплой Artist Map на VPS (Timeweb)

Инструкция для production-развёртывания через Docker Compose: PostgreSQL, FastAPI и статический фронтенд за nginx.

## Архитектура

| Сервис | Контейнер | Порт |
|--------|-----------|------|
| PostgreSQL 16 | `artist-map-postgres` | только внутри Docker-сети |
| API (uvicorn) | `artist-map-api` | 8000 (внутри сети) |
| Web (nginx + React build) | `artist-map-web` | **80** (публичный) |

Пользователь открывает `http://<IP>/` — nginx отдаёт фронтенд и проксирует `/api/` на backend.

## Требования к серверу

- Ubuntu 22.04+ / Debian 12+ (или другой Linux с Docker)
- RAM от 2 GB (граф ~12k артистов)
- Диск от 5 GB
- Открыт входящий порт **80** (и 443 после настройки SSL)

## Подготовка сервера (один раз)

```bash
ssh root@<IP_СЕРВЕРА>

# Docker (если ещё не установлен)
curl -fsSL https://get.docker.com | sh

# Каталог приложения
mkdir -p /opt/artist_map/backups
```

Пароль root и секреты **не храните в репозитории**. Используйте менеджер паролей и файл `.env` только на сервере.

## Файлы деплоя в репозитории

- `docker-compose.prod.yml` — production-стек
- `Dockerfile` — backend + Alembic + uvicorn
- `frontend/Dockerfile` — сборка Vite и nginx
- `.env.production.example` — шаблон переменных окружения
- `scripts/deploy_server.sh` — сборка и запуск на сервере
- `scripts/remote_deploy.py` — автоматический деплой с локальной машины по SSH

## Переменные окружения (`.env` на сервере)

Скопируйте шаблон и задайте значения:

```bash
cp .env.production.example .env
nano .env
```

| Переменная | Описание |
|------------|----------|
| `POSTGRES_PASSWORD` | Пароль БД (сложный, уникальный) |
| `DATABASE_URL` | URL с тем же паролем, хост `postgres` |
| `CORS_ORIGINS` | JSON-массив с публичным URL сайта |
| `ENVIRONMENT` | `production` |
| `YANDEX_MUSIC_TOKEN` | Опционально, для повторного импорта графа |

Пример `DATABASE_URL`:

```env
DATABASE_URL=postgresql+psycopg://artist_map:ВАШ_ПАРОЛЬ@postgres:5432/artist_map
```

## Перенос данных на прод

### Вариант A: дамп с локальной машины (рекомендуется)

На машине, где уже запущен локальный Postgres (`docker compose up -d`):

```bash
mkdir -p backups
docker exec artist-map-postgres pg_dump -U artist_map --no-owner --no-acl artist_map > backups/artist_map.sql
```

Скопируйте на сервер:

```bash
scp backups/artist_map.sql root@<IP>:/opt/artist_map/backups/
```

### Вариант B: импорт на сервере из Яндекс Музыки

Долгий процесс (десятки минут). После первого запуска только Postgres:

```bash
docker compose -f docker-compose.prod.yml run --rm api \
  python -m graph_builder.build_graph --artist "Oxxxymiron" --depth 3 --clear
```

## Ручной деплой на сервере

1. Загрузите код в `/opt/artist_map` (git clone, rsync или архив).

2. Положите дамп в `backups/artist_map.sql` (если переносите данные).

3. Создайте `.env` из `.env.production.example`.

4. Запустите:

```bash
cd /opt/artist_map
chmod +x scripts/deploy_server.sh deploy/entrypoint-api.sh
sed -i 's/\r$//' scripts/deploy_server.sh deploy/entrypoint-api.sh

# Первый деплой с восстановлением БД
RESTORE_DB=1 bash scripts/deploy_server.sh
```

Повторный деплой (без перезаписи БД):

```bash
bash scripts/deploy_server.sh
```

## Автоматический деплой с локальной Windows/Linux

Установите зависимость:

```bash
pip install paramiko
```

Создайте дамп и отправьте проект на сервер:

```powershell
$env:DEPLOY_SSH_PASSWORD = "<пароль_ssh>"
python scripts/remote_deploy.py --host 31.130.133.28
```

Повторно без пересоздания дампа:

```powershell
python scripts/remote_deploy.py --skip-dump
```

Скрипт: упаковывает проект → загружает по SSH → ставит Docker (если нужно) → собирает образы → восстанавливает БД → проверяет `/api/v1/health`.

## Проверка после деплоя

```bash
# На сервере
curl -s http://127.0.0.1/api/v1/health
curl -s "http://127.0.0.1/api/v1/artists/search?q=oxxx"

# С вашего ПК
curl -s http://<IP>/api/v1/health
```

Ожидаемый ответ health:

```json
{"status":"ok","app":"Artist Map"}
```

В браузере: `http://<IP>/`

## Полезные команды

```bash
cd /opt/artist_map

# Логи
docker compose -f docker-compose.prod.yml logs -f api
docker compose -f docker-compose.prod.yml logs -f web

# Перезапуск
docker compose -f docker-compose.prod.yml restart

# Остановка
docker compose -f docker-compose.prod.yml down

# Бэкап БД на сервере
docker compose -f docker-compose.prod.yml exec -T postgres \
  pg_dump -U artist_map --no-owner --no-acl artist_map > backups/artist_map-$(date +%F).sql
```

## Обновление версии

1. Загрузите новый код в `/opt/artist_map`.
2. `docker compose -f docker-compose.prod.yml build`
3. `docker compose -f docker-compose.prod.yml up -d`

Миграции применяются автоматически при старте контейнера `api` (`alembic upgrade head`).

## HTTPS (опционально)

Для домена можно поставить Caddy или Certbot перед nginx. После получения сертификата добавьте `https://ваш-домен` в `CORS_ORIGINS` и перезапустите API:

```bash
docker compose -f docker-compose.prod.yml up -d api
```

## Безопасность

- Смените пароль root после первого входа, настройте вход по SSH-ключу и отключите парольный вход.
- Не коммитьте `.env` и дампы БД в git.
- Используйте отдельный сильный `POSTGRES_PASSWORD` на проде.
- Ограничьте доступ к порту 5432 извне (в production Postgres не пробрасывается на хост).

## Устранение неполадок

| Симптом | Решение |
|---------|---------|
| `502` на `/api/` | `docker compose ... logs api`, дождитесь старта Postgres |
| Пустой поиск артистов | Проверьте, что `RESTORE_DB=1` выполнялся и дамп не пустой |
| CORS в браузере | Добавьте точный URL в `CORS_ORIGINS` |
| Порт 80 занят | `ss -tlnp \| grep :80`, остановите конфликтующий сервис |
