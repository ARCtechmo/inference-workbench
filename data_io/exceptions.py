"""Exceptions for the data_io layer."""


class DataLoadError(Exception):
    """Raised when a data file cannot be loaded.

    Covers: file missing, unreadable (permissions), or unparseable.
    Carries a human-readable message suitable for display in the app layer.
    """
