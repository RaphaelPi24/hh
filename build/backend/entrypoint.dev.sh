#!/usr/bin/env bash
# peewee migrate

#until pg_isready -h db -U $flaskuser; do
#  sleep 2
#done
#python app.py
python -c "
from migrations import run_migrations
run_migrations()
"

# Запускаем основное приложение
exec python app.py