install-dev:
	python3 -m venv .venv
	. .venv/bin/activate
	pip3 install -r requirements.dev.txt

install:
	pip3 install -r requirements.txt

ci:
	pep8 mainapp/ --ignore=E501
	pip3 install ddt
	python3 manage.py test tests

run:
	python3 manage.py runserver

chpwd:
	python3 manage.py changepassword admin

