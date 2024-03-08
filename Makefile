.PHONY: test dev lint

all: lint test

install:
	python -m pip install --upgrade pip
	pip install poetry
	poetry install

test:
	poetry run pytest -v

dev:
	python ./src/translator.py ./examples/test.lsp
	python ./src/machine.py ./out.o.json ./examples/test.txt

debug:
	python ./src/translator.py ./examples/test.lsp
	python ./src/machine.py ./out.o.json ./examples/test.txt -d

interactive:
	python ./src/translator.py ./examples/test.lsp
	python ./src/machine.py ./out.o.json ./examples/test.txt -d -i

lint:
	poetry run mypy ./src/machine.py
	poetry run mypy ./src/translator.py
	poetry run ruff check ./src

fix:
	poetry run ruff format ./src
	poetry run ruff check --fix ./src

test-update-golden:
	poetry run pytest . -v --update-goldens