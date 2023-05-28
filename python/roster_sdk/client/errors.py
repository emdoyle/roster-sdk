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


class TeamMemberNotFound(RosterClientException):
    """Exception raised when a team member is not found."""

    def __init__(
        self, message="The requested team member was not found.", details=None
    ):
        super().__init__(message, details)


class TeamMemberNotInPeerGroup(RosterClientException):
    """Exception raised when the requested team member is not in the agent's peer group."""

    def __init__(
        self, message="The requested team member is not in the agent's peer group."
    ):
        super().__init__(message)
