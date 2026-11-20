# --- React UI (frontend/) -> mainapp/static/mainapp/dist ---------------------
FROM node:22-slim AS frontend
WORKDIR /build/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

# --- Django application ----------------------------------------------------
FROM python:3.12-slim

LABEL maintainer="Marcin Bielak <marcin.bieli@gmail.com>"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf8 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DJANGO_STATIC_ROOT=/app/staticfiles \
    DJANGO_DB_PATH=/data/db.sqlite3

WORKDIR /app

COPY requirements.txt requirements.dev.txt ./
ARG INSTALL_DEV=0
RUN if [ "$INSTALL_DEV" = "1" ]; then pip install -r requirements.dev.txt; \
    else pip install -r requirements.txt; fi

COPY . .
COPY --from=frontend /build/mainapp/static/mainapp/dist /app/mainapp/static/mainapp/dist

RUN DJANGO_SECRET_KEY=collectstatic python manage.py collectstatic --noinput \
    && useradd --uid 1000 --create-home app \
    && mkdir -p /data \
    && chown -R app:app /data \
    && sed -i "s/\r$//" docker/entrypoint.sh \
    && chmod +x docker/entrypoint.sh

USER app
EXPOSE 8000
VOLUME ["/data"]
ENTRYPOINT ["docker/entrypoint.sh"]
CMD ["gunicorn", "FreeItLessons.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--access-logfile", "-"]
