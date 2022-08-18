.PHONY: init test coverage ci publish docs

init:
	pip install -r requirements.txt

test:
	pip install -qq --upgrade tox
	tox -p

coverage:
	pytest --cov-config .coveragerc --verbose --cov-report term --cov-report xml --cov=illumio tests

ci:
	pytest tests --junitxml=report.xml --assert=plain

publish:
	pip install --upgrade twine
	python -m build .
	twine upload dist/*
	rm -rf build dist illumio.egg-info

docs:
	cd docs && make html
	@echo "\033[95m\n\nBuild successful! View the docs homepage at docs/_build/html/index.html.\n\033[0m"
