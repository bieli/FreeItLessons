FROM avnergoncalves/ubuntu-python3.5

MAINTAINER Marcin Bielak <marcin.bieli@gmail.com>

# Enable production settings by default; for development, this can be set to 
# `false` in `docker run --env`
ENV DJANGO_PRODUCTION=true

# Set terminal to be noninteractive
ENV DEBIAN_FRONTEND noninteractive

ENV PYTHONIOENCODING=utf8

RUN apt-get update && apt-get install -y \
    python-setuptools \
    gcc \
    gettext \
    mysql-client libmysqlclient-dev \
    postgresql-client libpq-dev \
    sqlite3 \
    python3-pip \
    python3-venv \
    libffi-dev \
    libssl-dev \
    libpython3-dev \
    libcurl4-openssl-dev \
	--no-install-recommends && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
COPY . .
RUN pip3 install -U pip setuptools
RUN pip3 install -r requirements.txt

EXPOSE 8000
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]

