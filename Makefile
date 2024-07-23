.PHONY: all format lint test tests free_tests integration_tests help format

# Default target executed when no arguments are given to make.
all: help

test:
	python3 -m unittest tests.all_test_runner

test_free:
	python3 -m unittest tests.free_test_runner

test_integration:
	python3 -m unittest tests.test_integration.paid_integration_test_runner

test_unit:
	python3 -m unittest tests.unit_test_runner

init:
	poetry install --with dev
	./scripts/setup_precommit.sh

######################
# LINTING AND FORMATTING
######################

format:
	black . --fast

######################
# DOCUMENTATION
######################

docs_preview:
	BUNDLE_GEMFILE=docs/Gemfile bundle exec jekyll serve --source docs/

docs_refresh:
	python3 scripts/refresh_class_documentation.py
	python3 scripts/refresh_function_documentation.py

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
	@echo 'test_free................... - run all free unit and integration tests'
	@echo 'test_unit................... - run all free unit tests'
	@echo 'test_integration............ - run all integration tests'	