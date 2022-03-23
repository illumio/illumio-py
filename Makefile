.PHONY: init test coverage ci

init:
	pip install -r requirements.txt tox

test:
	tox -p

coverage:
	pytest --cov-config .coveragerc --verbose --cov-report term --cov-report xml --cov=illumio tests

ci:
	pytest tests --junitxml=report.xml
