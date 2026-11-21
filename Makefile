.PHONY: install-dev install lint test ci run chpwd migrate docker-up docker-test regression \
	frontend-install frontend-build frontend-dev frontend-test e2e regression-ui

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

run: migrate frontend-build
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

# server contract of the React UI branch vs the jQuery UI branch (AJAX, files, admin, DB)
regression-ui:
	BASELINE_MODE=modern LEGACY_REF=$${BASE_REF:-f88c010dc8699525694a17bd793ee35c00409b4a} \
	EXPECTED_FILE=expected_differences.react-ui.json regression/run.sh

# React UI (needs Node >= 22; or use: docker compose run --rm frontend-tests)
frontend-install:
	cd frontend && npm ci

frontend-build:
	cd frontend && npm run build

frontend-dev:
	cd frontend && npm run dev

frontend-test:
	cd frontend && npm test

# browser tests: the same Playwright spec against the jQuery UI (BASE_REF) and the React UI
e2e:
	e2e/run.sh
