# !/usr/bin/env bash

sleep 5
if ! alembic check | grep -q 'No new upgrade operations detected.'; then
    alembic revision --autogenerate -m "migration"
else
    echo "No new upgrade operations detected."
fi

alembic upgrade head
python3 init_data.py
gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000