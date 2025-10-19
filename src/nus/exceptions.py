"""Custom exceptions for the news curation system."""


class NusError(Exception):
    """Base exception for all nus errors."""

    pass


class FetchError(NusError):
    """Error during RSS feed fetching."""

    pass


class AnalysisError(NusError):
    """Error during article analysis."""

    pass


class ConfigError(NusError):
    """Error in configuration."""

    pass


class RenderError(NusError):
    """Error during HTML rendering."""

    pass
