class RosterClientException(Exception):
    """Base exception class for roster client-related errors."""

    def __init__(self, message="An unexpected error occurred.", details=None):
        super().__init__(message, details)


class RosterConnectionError(RosterClientException):
    """Exception raised when a connection error occurs."""

    def __init__(self, message="A connection error occurred.", details=None):
        super().__init__(message, details)


class ResourceNotFound(RosterClientException):
    """Exception raised when a resource is not found."""

    def __init__(self, message="The requested resource was not found.", details=None):
        super().__init__(message, details)
