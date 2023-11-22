# !/usr/bin/env bash

alembic revision --autogenerate -m "Initial commit"
sleep 5
alembic upgrade head
sleep 5
python3 init_data.py
