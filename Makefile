.PHONY: init test coverage ci publish

init:
	pip install -r requirements.txt

test:
	pip install -qq --upgrade tox
	tox -p

coverage:
	pytest --cov-config .coveragerc --verbose --cov-report term --cov-report xml --cov=illumio tests

ci:
	pytest tests --junitxml=report.xml

publish:
	pip install --upgrade twine
	python -m build .
	twine upload dist/*
	rm -rf build dist illumio.egg-info
