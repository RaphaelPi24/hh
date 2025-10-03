#!/usr/bin/env bash

python -c "
from migrations import run_migrations
run_migrations()
"

exec gunicorn -c gunicorn.py -w 1 app:app