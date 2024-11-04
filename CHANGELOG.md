# @a-s-g93/neo4j-runway

## Next

### Fixed

### Changed

### Added

## 0.14.0

### Fixed

* Fix bug where patching previous valid nodes into an invalid data model would throw an error

### Changed

* Add comma separator for numbers in `GraphEDA` report
* Remove deprecated `IngestionGenerator` class
* Update README to include `GraphEDA` module
* Remove images/
* Mild refactor of `Property.type` validation

### Added

* Add `relType` to relationship properties section of `GraphEDA` module
* Add arguments to `GraphEDA.run()` to allow for more flexibility in chosen methods and parameters
* Add arguments to `GraphEDA.node_degrees` to allow for better result filtering
* Add arguments to `GraphEDA.run()` and `GraphEDA.create_eda_report()` to control directly returning result

## 0.13.1

### Fixed

* Remove `dotenv` package dependency from `Neo4jGraph` and `GraphEDA`

## 0.13.0

### Added

* `GraphEDA` module that gathers analytics and provides a report on the specified database
* `gds_version` property to `Neo4jGraph`
* Examples demonstrating how to use the new `GraphEDA` module

## 0.12.0

### Fixed

* Fix bug where `use_cases` arg in `UserInput` not accounted for.

### Changed

* Change initial `DataModel` generation logic to first generate nodes, then generate relationships
* Updated examples
* Remove `use_yaml_data_model` arg from `DataModel` generation methods, as it is no longer relevant
* Update `DataModel`, `Node`, `Relationship` and `Property` validation logic to better utilize `Pydantic` library
* Update `Instructor` dependency to v1.5.2
* Simplify LLM retry logic by better utilizing `Instructor` library
* Update printed results and progress of `DataModel` generating methods to be prettier
* Update Graphviz visual from `DataModel.visualize()`

### Added

* Add `DataModel` validator to check for parallel relationships
* Add `allow_parallel_relationships` arg to `DataModel` generating methods
* Add `apply_neo4j_naming_conventions` arg to `DataModel` generating methods
* Add `get_schema()` to `DataModel`, `Node`, `Relationship` and `Property` to output a text version of schema

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
