.PHONY: all format lint test tests free_tests integration_tests help format

# Default target executed when no arguments are given to make.
all: help

test tests:
	python3 -m unittest tests.all_test_runner

free_tests:
	python3 -m unittest tests.free_test_runner

integration_tests:
	python3 -m unittest tests.test_integration.paid_integration_test_runner

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

######################
# HELP
######################

help:
	@echo '----'
	@echo 'init                         - initialize the repo for development (must still install Graphviz separately)'
	@echo 'format                       - run code formatters'
	@echo 'test                         - run all unit and integration tests'
	@echo 'tests                        - run all unit and integration tests'
	@echo 'integration_tests            - run all integration tests'
	@echo 'free_tests                   - run all free unit and integration tests'
	@echo 'docs_preview                 - preview the local documentation site'
