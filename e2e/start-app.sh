#!/bin/sh
# Starts one application instance (baseline or candidate) for the browser tests.
set -e
python manage.py migrate --noinput
python manage.py shell -c "$(cat /regression/prepare_db.py)"
exec gunicorn FreeItLessons.wsgi:application --bind 0.0.0.0:8000 --workers 3
