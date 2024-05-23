#!/bin/bash
echo "Running entrypoint.sh"

export PYTHONPATH=$(pwd)
python -m alembic upgrade head
python app/initial_data.py
uvicorn main:app --host 0.0.0.0 --port ${PORT:-80}