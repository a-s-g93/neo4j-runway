"""
This file contains all custom exceptions found in Runway.
"""


class RunwayError(Exception):
    """
    Global error for Runway.
    """


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
