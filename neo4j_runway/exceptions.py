"""
This file contains all custom exceptions found in Runway.
"""


class RunwayError(Exception):
    """
    Global error for Runway.
    """


class RunwayPydanticValidationError(ValueError):
    """Global error for handling Pydantic errors in Runway"""


class Neo4jVersionError(RunwayError):
    """Exception raised when Neo4j version does not meet minimum requirements."""

    pass


class APOCVersionError(RunwayError):
    """Exception raised when APOC version does not meet minimum requirements."""

    pass


class APOCNotInstalledError(RunwayError):
    """Exception raised when APOC is required for operation, but not installed on Neo4j instance."""

    pass


class InvalidDataModelGenerationError(RunwayError):
    """Exception raised when an invalid data model is returned by an LLM after all retry attempts have been exhausted."""

    pass


class InvalidArrowsDataModelError(RunwayError):
    """Exception raised when an arrows.app data model is unable to be parsed into a Runway core data model."""

    pass


class InvalidSolutionsWorkbenchDataModelError(RunwayError):
    """Exception raised when a Solutions Workbench data model is unable to be parsed into a Runway core data model."""

    pass


class DataNotSupportedError(RunwayError):
    """Exception raised when an unsupported data format is given to a DataLoader class."""

    pass


class LoadCSVCypherGenerationError(RunwayError):
    """Exception raised when no standard clause can be constructed from provided arguments."""

    pass


class PandasDataSummariesNotGeneratedError(RunwayError):
    """Exception raised when the Discovery class 'run' method is ran and Pandas data summaries are not generated."""

    pass


class InvalidSourceNameError(RunwayPydanticValidationError):
    """Exception raised when an invalid `source_name` is provided."""

    pass


class NonuniqueNodeError(RunwayPydanticValidationError):
    """Exception raised when a node has no unique properties."""

    pass


class InvalidColumnMappingError(RunwayPydanticValidationError):
    """Exception raised when a property is mapped to either a missing or invalid column."""

    pass


class MissingSourceNodeError(RunwayPydanticValidationError):
    """Exception raised when a relationship has a source node that is not present in the data model."""

    pass


class MissingTargetNodeError(RunwayPydanticValidationError):
    """Exception raised when a relationship has a target node that is not present in the data model."""

    pass


class SameSourceAndTargetNodeWithNoAliasError(RunwayPydanticValidationError):
    """Exception raised when a relationship has source and target nodes with the same label, but there is no unique property alias named."""

    pass


class PropertyAliasNotFoundInFileError(RunwayPydanticValidationError):
    """Exception raised when a relationship and its source or target node are from different files and the unique node property alias is not found in the node source file."""

    pass


class PropertyAliasMissingError(RunwayPydanticValidationError):
    """Exception raised when a relationship and its source or target node are from different files and the unique node property has no named alias."""

    pass


class SharedColumnMappingError(RunwayPydanticValidationError):
    """Exception raised when a property column mapping is shared between many nodes or relationships."""

    pass
