#!/bin/bash
echo "Running entrypoint.sh"

export PYTHONPATH=$(pwd)
# generate migration with random generated message
python -m alembic upgrade head
python app/initial_data.py

exec uvicorn main:app --host 0.0.0.0 --port ${PORT}