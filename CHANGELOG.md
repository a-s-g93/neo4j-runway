# @a-s-g93/neo4j-runway

## Next

### Fixed

### Changed

### Added

## 0.9.0

### Fixed

### Changed

### Added

## 0.8.1

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
