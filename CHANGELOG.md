# @a-s-g93/neo4j-runway

## Next

### Fixed

* Fix bug where `use_cases` arg in `UserInput` not accounted for.

### Changed

### Added

## 0.11.0

### Changed

* Removed `kwargs` from LLM classes and replaced with `llm_init_params` to provide parameters that should be passed to the LLM constructor.

### Added

* Azure OpenAI integrations for Discovery and Data Modeling: `AzureOpenAIDiscoveryLLM` and `AzureOpenAIDataModelingLLM`
* Added example that used Azure OpenAI models

## 0.10.0

### Fixed

* Initial data modeling takes into account entity pool generation step
* Fixed bug where some filepaths break saving content to file

### Changed

* All data input to Discovery is converted to TableCollection class
* Discovery generated content is contained in Table on `discovery_content` attribute
* Discovery file output is handled on Table and TableCollection classes instead of Discovery class
* Data Modeling prompts have been significantly refactored and organized into a consistent format

### Added

* Add `verbose` arg to `PyIngest` to suppress progress printing
* Multi file support for Discovery process (EXPERIMENTAL)
  * parameters in `discovery.run()` and `discovery.run_async()` to control process
  * async capability to improve response time for multi file
* Multi file support for Data Modeling process (EXPERIMENTAL)
* Cypher generation support for relationships spanning across different files

## 0.9.1

### Fixed

* Fix bug in LoadCSVCodeGenerator

### Added

* Unit tests for LoadCSVCodeGenerator and StandardCypherCodeGenerator classes

## 0.9.0

### Fixed

* pre-commit hooks now work properly and utilize ruff and mypy instead of black

### Changed

* Refactor LLM class into base class with DiscoveryLLM and DataModelingLLM child classes for each LLM integration

* Restructure and refactor tests directory to mirror the neo4j_runway package structure

* Implement pytest to handle testing

### Added

* Implement GitHub actions to automate unit and integration testing on PR

* Implement GitHub actions to automate ruff and mypy checks on PR

* Implement strict style guides utilizing ruff and mypy

* Add Neo4jGraph module to handle database connections. This will be used in a future EDA module.

* Add changelog to track changes better.

* Use cases can now be added to the UserInput object to be considered during Discovery and Graph Data Modeling

* Refactor discovery and data modeling prompts

* Added additional validation checks to DataModel

* Implement chain-of-thought reasoning for initial data model generation. This improves responses by:

  * Multi-hop traversals generated more reliably when appropriate

  * Constraints generated more reliably
