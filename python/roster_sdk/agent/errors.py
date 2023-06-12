class RosterAgentException(Exception):
    """Base class for all Roster Agent exceptions"""

    def __init__(self, message):
        self.message = message


class RosterAgentTaskException(RosterAgentException):
    """Base class for all Roster Agent task exceptions"""


class RosterAgentTaskNotFound(RosterAgentTaskException):
    """Raised when a task is not found"""


class RosterAgentTaskAlreadyExists(RosterAgentTaskException):
    """Raised when a task already exists"""
