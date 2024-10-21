class RunwayWarning(Warning):
    """Global Warning for Runway."""


class ExperimentalFeatureWarning(RunwayWarning):
    """Warning raised when an experimental feature is being utilized."""
