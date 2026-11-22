#!/bin/sh
# Seeds the persistent volume with the bundled demo database on first start
# and applies migrations before handing over to the main process.
set -e

# Without DJANGO_SECRET_KEY a random key is generated once and kept next to the
# database (sessions survive restarts, every installation has its own key).
if [ -z "$DJANGO_SECRET_KEY" ]; then
    key_file="$(dirname "${DJANGO_DB_PATH:-/data/db.sqlite3}")/.django-secret-key"
    if [ ! -s "$key_file" ]; then
        echo "entrypoint: generating a new secret key in $key_file"
        (umask 077 && python -c 'import secrets; print(secrets.token_urlsafe(50))' > "$key_file")
    fi
    DJANGO_SECRET_KEY="$(cat "$key_file")"
    export DJANGO_SECRET_KEY
fi
if [ -n "$DJANGO_DB_PATH" ] && [ ! -f "$DJANGO_DB_PATH" ] && [ -f /app/db.sqlite3 ]; then
    echo "entrypoint: seeding $DJANGO_DB_PATH from the bundled demo database"
    cp /app/db.sqlite3 "$DJANGO_DB_PATH"
fi
python manage.py migrate --noinput
exec "$@"
