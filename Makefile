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
	python ./src/translator.py ./examples/test.lsp -d
	python ./src/machine.py ./out.o.json ./examples/test.txt -d

interactive:
	python ./src/translator.py ./examples/test.lsp -d
	python ./src/machine.py ./out.o.json ./examples/test.txt -d -i

cat:
	python ./src/translator.py ./examples/cat.lsp
	python ./src/machine.py ./out.o.json ./examples/test.txt -d

bubble:
	python ./src/translator.py ./examples/bubble.lsp
	python ./src/machine.py ./out.o.json ./examples/test.txt

cache:
	python ./src/translator.py ./examples/test.lsp
	python ./src/machine.py ./out.o.json ./examples/test.txt -m

lint:
	poetry run mypy ./src/machine.py
	poetry run mypy ./src/translator.py
	poetry run ruff check ./src

fix:
	poetry run ruff format ./src
	poetry run ruff check --fix ./src

test-update-golden:
	poetry run pytest . -v --update-goldens