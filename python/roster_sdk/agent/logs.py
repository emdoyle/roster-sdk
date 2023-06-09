import logging

from roster_sdk import constants
from roster_sdk.config import AgentConfig

logger = logging.getLogger(constants.AGENT_LOGGER_NAME)
logger.setLevel(logging.DEBUG)

logs_enabled = False


def setup_logging():
    global logs_enabled
    if logs_enabled:
        # logging already setup,
        # don't add new handlers
        return
    config = AgentConfig.from_env()
    log_file = config.roster_agent_log_file
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_log_format = "%(message)s"
    file_format = logging.Formatter(file_log_format)
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)

    logs_enabled = True


def get_roster_agent_logger():
    setup_logging()
    return logger
