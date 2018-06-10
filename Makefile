.PHONY: clean doc help lint prepare-dev python-reqs run setup test

VENV_NAME?=.venv
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

VENV = .venv
export VIRTUAL_ENV := $(abspath ${VENV})
export PATH := ${VIRTUAL_ENV}/bin:${PATH}

${VENV}:
	python3.6 -m venv $@

# Requirements are in setup.py, so whenever setup.py is changed, re-run installation of dependencies.
venv: $(VENV_NAME)/bin/activate
$(VENV_NAME)/bin/activate: requirements.txt
	test -d $(VENV_NAME) || virtualenv -p python3 $(VENV_NAME)
	${PYTHON} -m pip install -U pip
	${PYTHON} -m pip install -e .
	touch $(VENV_NAME)/bin/activate

clean:
	rm -rf ${CLEANUP}

doc:
	@echo "FIXME"
	$(VENV_ACTIVATE) && cd docs; make html

lint: venv
	${PYTHON} -m pylint
	${PYTHON} -m mypy

prepare-dev:
	sudo apt-get -y install python3 python3-pip
	python3 -m pip install virtualenv
	make venv

python-reqs: requirements.txt | ${VENV}
	pip install --upgrade -r requirements.txt

run: venv
	${PYTHON} manage.py

setup: python-reqs git-config | .git ${VENV}

CLEANUP = *.pyc

test: venv
	echo "FIXME"
	${PYTHON} -m pytest
#$(PYTHON_BIN)/nosetests -v --with-coverage --cover-package=$(PROJECT) --cover-inclusive --cover-erase tests
