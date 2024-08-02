# @a-s-g93/neo4j-runway

## Next

### Fixed

### Changed

* Refactor LLM class into base class with DiscoveryLLM and DataModelingLLM child classes for each LLM integration

* pre-commit hooks now work properly and utilize ruff instead of black

* Restructure and refactor tests directory to mirror the neo4j_runway package structure

* Implement pytest to handle testing

### Added

* Add Neo4jGraph module to handle database connections. This will be used in a future EDA module.

* Add changelog to track changes better.

* Use cases can now be added to the UserInput object to be considered during Discovery and Graph Data Modeling

* Refactor discovery and data modeling prompts

* Added additional validation checks to DataModel

* Implement chain-of-thought reasoning for initial data model generation. This improves responses by:

  * Multi-hop traversals generated more reliably when appropriate

  * Constraints generated more reliably
