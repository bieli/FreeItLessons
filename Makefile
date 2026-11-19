.PHONY: install-dev install lint test ci run chpwd migrate docker-up docker-test regression

install-dev:
	python3.12 -m venv .venv
	.venv/bin/pip install -r requirements.dev.txt

install:
	pip3 install -r requirements.txt

lint:
	pycodestyle mainapp/ tests/ FreeItLessons/

test:
	python3 manage.py makemigrations --check --dry-run
	python3 manage.py collectstatic --noinput -v0
	python3 manage.py test tests

ci: lint test

migrate:
	DJANGO_DEBUG=1 python3 manage.py migrate

run: migrate
	DJANGO_DEBUG=1 python3 manage.py runserver

chpwd:
	DJANGO_DEBUG=1 python3 manage.py changepassword admin

docker-up:
	docker compose up --build

docker-test:
	docker compose run --build --rm tests

# legacy (Python 3.7 + Django 1.11) vs current tree - see regression/README.md
regression:
	regression/run.sh
