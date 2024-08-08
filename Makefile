.PHONY: all format lint test tests free_tests integration_tests help format

# Default target executed when no arguments are given to make.
all: help

test:
	pytest tests

test_integration:
	poetry run pytest tests/integration

test_unit:
	poetry run pytest tests/unit

init:
	poetry install --with dev
	pre-commit install

######################
# LINTING AND FORMATTING
######################

format:
	poetry run ruff format

######################
# DOCUMENTATION
######################

docs_preview:
	BUNDLE_GEMFILE=docs/Gemfile bundle exec jekyll serve --source docs/

docs_refresh:
	python3 scripts/refresh_class_documentation.py
	python3 scripts/refresh_function_documentation.py
	python3 scripts/update_docs_version.py

docs_add_example:
	 python3 scripts/add_example_to_docs.py --notebook_path=$(file_path)

######################
# HELP
######################

help:
	@echo '----'
	@echo 'init........................ - initialize the repo for development (must still install Graphviz separately)'
	@echo 'docs_add_example............ - args: file_path, add specified example notebook from the a-s-g93/neo4j-runway-examples/main github repo'
	@echo 'docs_preview................ - preview the local documentation site'
	@echo 'docs_refresh................ - refresh documentation for all public classes and functions'
	@echo 'format...................... - run code formatters'
	@echo 'test........................ - run all unit and integration tests'
	@echo 'test_unit................... - run all free unit tests'
	@echo 'test_integration............ - run all integration tests'
