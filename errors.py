class GradebookError(Exception):
    """Base exception for gradebook errors."""


class ValidationError(GradebookError):
    """Raised when input validation fails."""


class NotFoundError(GradebookError):
    """Raised when a requested resource is not found."""


class ConflictError(GradebookError):
    """Raised when a resource conflicts with existing data."""