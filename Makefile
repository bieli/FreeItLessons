install-dev:
	python3 -m venv .venv
	. .venv/bin/activate
	pip3 install -r requirements.dev.txt

install:
	pip3 install -r requirements.txt

ci:
	pip3 install ddt
	python3 -m unittest tests/*.py

run:
	python3 manage.py runserver

chpwd:
	python3 manage.py changepassword admin

