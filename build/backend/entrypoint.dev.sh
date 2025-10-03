#!/usr/bin/env bash

python -c "
from migrations import run_migrations
run_migrations()
"

exec python app.py