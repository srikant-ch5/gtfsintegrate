.PHONY: clean doc help lint prepare-dev python-reqs run setup test

VENV_NAME?= venv
VENV_ACTIVATE=. $(VENV_NAME)/bin/activate
PYTHON=${VENV_NAME}/bin/python3
PYTHON_BIN := $(VENV_NAME)/bin

.DEFAULT: help

help:
	@echo "make ${VENV}"
	@echo "		make a virtualenv in the base directory (see VENV)"
	@echo "make clean"
	@echo "		remove intermediate files (see CLEANUP)"
	@echo "make doc"
	@echo "		build sphinx documentation"
	@echo "make help"
	@echo "		show help message"
	@echo "make lint"
	@echo "		run lint"
	@echo "make prepare-dev"
	@echo "		prepare development environment, use only once"
	@echo "make python-reqs"
	@echo "		install python packages in requirements.txt"
	@echo "make run"
	@echo "		run project"
	@echo "make setup"
	@echo "		make python-reqs"
	@echo "make test"
	@echo "		run tests"

.git:
	git init

VENV = venv
export VIRTUAL_ENV := $(abspath ${VENV})
export PATH := ${VIRTUAL_ENV}/bin:${PATH}

${VENV}:
	python3 -m venv $@

# Requirements are in requirements.txt, so whenever requirements.txt is changed, re-run installation of dependencies.
venv:
	test -d $(VENV_NAME) || virtualenv -p python3 $(VENV_NAME)
	${PYTHON} -m pip install --upgrade pip
	${PYTHON} -m pip install -r requirements.txt
	touch $(VENV_NAME)/bin/activate

clean:
	rm -rf ${CLEANUP}
	rm -rf venv

doc:
	@echo "FIXME"
	$(VENV_ACTIVATE) && cd docs; make html

lint: venv
	${PYTHON} -m pycodestyle --show-source --first --show-pep8 **/*.py
	${PYTHON} -m pylint **/*.py
	${PYTHON} -m mypy

lint-fix: venv
	${PYTHON} -m autopep8 --aggressive --aggressive --recursive --in-place --max-line-length 139 **/*.py

# add geos/gdal libs and requirements
prepare-dev:
	sudo apt-get --yes install binutils libproj-dev gdal-bin libgeoip1 python-gdal
	sudo apt-get --yes install python3 python3-pip virtualenv python3-dev \
		postgresql postgresql-contrib postgis libpq-dev libgeos-dev \
		redis-server libffi6 libffi-dev
	python3 -m pip install virtualenv
	make venv

python-reqs: requirements.txt | ${VENV}
	pip install --upgrade -r requirements.txt

run: venv
	${PYTHON} manage.py makemigrations
	${PYTHON} manage.py migrate
	${PYTHON} manage.py runserver

setup: python-reqs git-config | .git ${VENV}

CLEANUP = *.pyc

test: venv
	echo "FIXME"
	${PYTHON} -m pytest
#$(PYTHON_BIN)/nosetests -v --with-coverage --cover-package=$(PROJECT) --cover-inclusive --cover-erase tests
