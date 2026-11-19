#!/bin/sh
set -e
python manage.py migrate --noinput
python manage.py shell -c "$(cat /regression/schema_check.py)"
python manage.py shell -c "$(cat /regression/prepare_db.py)"
exec gunicorn FreeItLessons.wsgi:application --bind 0.0.0.0:8000 --workers 2 --access-logfile -
