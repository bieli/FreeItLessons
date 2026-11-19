#!/bin/sh
# Seeds the persistent volume with the bundled demo database on first start
# and applies migrations before handing over to the main process.
set -e
if [ -n "$DJANGO_DB_PATH" ] && [ ! -f "$DJANGO_DB_PATH" ] && [ -f /app/db.sqlite3 ]; then
    echo "entrypoint: seeding $DJANGO_DB_PATH from the bundled demo database"
    cp /app/db.sqlite3 "$DJANGO_DB_PATH"
fi
python manage.py migrate --noinput
exec "$@"
