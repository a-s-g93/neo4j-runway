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
