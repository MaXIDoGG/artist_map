# Artist Map

Artist Map строит граф коллабораций артистов и показывает, через сколько фитов один артист связан с другим.

## Стек

- Backend: FastAPI, SQLAlchemy, Alembic, PostgreSQL, NetworkX.
- Import pipeline: Yandex Music API и seed из старого GraphML.
- Frontend: React, Vite, TypeScript, D3.

## Быстрый Запуск

```bash
cp .env.example .env
docker compose up -d
python -m pip install -r requirements.txt
alembic upgrade head
python -m graph_builder.build_graph --graphml data/graph.graphml --clear
uvicorn backend.api.main:app --reload
```

В отдельном терминале:

```bash
cd frontend
npm install
npm run dev
```

Frontend будет доступен на `http://localhost:5173`, backend API - на `http://127.0.0.1:8000/api/v1`.
Postgres из Docker пробрасывается на `localhost:5433`, чтобы не конфликтовать с локальным PostgreSQL на `5432`.

## Основные Команды

```bash
# Проверить backend
pytest

# Собрать frontend
cd frontend
npm run build

# Импортировать граф из Яндекс Музыки
python -m graph_builder.build_graph --artist "Oxxxymiron" --depth 2

# Экспортировать GraphML без записи в БД
python -m graph_builder.build_graph --artist "Oxxxymiron" --export-graphml data/graph.graphml
```

## API

- `GET /api/v1/health` - проверка сервиса.
- `GET /api/v1/artists/search?q=` - поиск артистов для автокомплита.
- `GET /api/v1/graph/path?source_id=&target_id=` - кратчайший путь между артистами.
- `GET /api/v1/graph/subgraph?artist_id=&depth=` - ближайшая окрестность артиста.

## Данные

Postgres является основным источником данных. Старый `data/graph.graphml` можно использовать как seed, чтобы быстро наполнить базу без повторного обхода Яндекс Музыки.
