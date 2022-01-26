.PHONY: build setup test build check upload upload-test

setup:
	@cp .pypirc-dist .pypirc

test:
	poetry install
	pytest ./tests

build:
	python setup.py bdist_wheel

check:
	twine check dist/*

upload: check
	twine upload --config-file .pypirc dist/*

upload-test: check
	twine upload --repository testpypi --config-file .pypirc dist/*
