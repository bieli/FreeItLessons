# Reference ("golden master") image of the LEGACY application:
# Python 3.7 + Django 1.11 with the third-party packages pinned exactly as the
# original requirements.txt resolved them. Used only by the regression harness.
FROM python:3.7-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf8

RUN pip install --no-cache-dir \
        "Django==1.11.23" \
        "django-bootstrap3==11.0.0" \
        "django-admin-sortable2==0.6.10" \
        "django-enumfield==1.5" \
        "django-lineage==0.2.0" \
    # legacy settings hardcode PYTHON_EXEC=/usr/bin/python3 for the code runner
    && ln -sf /usr/local/bin/python3 /usr/bin/python3

WORKDIR /app
COPY . .
EXPOSE 8000
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000", "--noreload"]
