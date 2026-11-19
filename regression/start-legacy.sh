#!/bin/sh
# Legacy settings hardcode BASE_DIR/db.sqlite3 - point it to the state volume.
set -e
ln -sf /state/db.sqlite3 /app/db.sqlite3
python manage.py shell -c "$(cat /regression/prepare_db.py)"
exec python manage.py runserver 0.0.0.0:8000 --noreload
