class RepositoryError(Exception):
    """Base repository failure."""


class RepositoryConflictError(RepositoryError):
    """The requested write conflicts with existing state."""


class RepositoryUnavailableError(RepositoryError):
    """The Azure dependency is temporarily unavailable."""
