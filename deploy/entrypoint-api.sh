#!/bin/sh
set -e

alembic upgrade head
exec uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --workers 2
