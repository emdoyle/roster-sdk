import logging
import logging.handlers

from roster_sdk import constants
from roster_sdk.agent.context import get_agent_activity_context
from roster_sdk.config import AgentConfig
from roster_sdk.models.api.activity import ActivityEvent, ActivityType

logger = logging.getLogger(constants.AGENT_LOGGER_NAME)
logger.setLevel(logging.DEBUG)

logs_enabled = False


def ensure_logging():
    global logs_enabled
    if logs_enabled:
        # logging already setup,
        # don't add new handlers
        return

    config = AgentConfig.from_env()
    log_file = config.roster_agent_log_file

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_log_format = "%(levelname)s:\t [log] %(message)s"
    console_format = logging.Formatter(console_log_format)
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    file_handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=1000000)
    file_handler.setLevel(logging.DEBUG)
    file_log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_format = logging.Formatter(file_log_format)
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)

    logs_enabled = True


def get_logger():
    ensure_logging()
    return logger


class ActivityLogger:
    def __init__(self):
        self.listeners = []

    def add_listener(self, listener):
        self.listeners.append(listener)

    def remove_listener(self, listener):
        self.listeners.remove(listener)

    def _notify_listeners(self, event: ActivityEvent):
        for listener in self.listeners:
            listener(event)

    def _send_event(self, event_type: ActivityType, message: str):
        context = get_agent_activity_context()
        if context is None:
            return
        agent_ctx, execution_ctx = context
        event = ActivityEvent(
            execution_id=execution_ctx.execution_id,
            execution_type=execution_ctx.execution_type,
            type=event_type,
            content=message,
            agent_context=agent_ctx,
        )
        self._notify_listeners(event)

    def thought(self, message: str):
        self._send_event(ActivityType.THOUGHT, message)

    def action(self, message: str):
        self._send_event(ActivityType.ACTION, message)


activity_logger = ActivityLogger()


# honor system singleton
def get_roster_activity_logger() -> ActivityLogger:
    return activity_logger
