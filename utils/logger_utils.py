# logger_utils.py

import logging
import os
from logging.handlers import RotatingFileHandler
from scripts.constants import (
    DEBUG_LOG_PATH,
    INFO_LOG_PATH,
    ERROR_LOG_PATH,
    LOG_FOLDER,
)

class LevelFilter(logging.Filter):
    def __init__(self, level):
        super().__init__()
        self.level = level
    def filter(self, record):
        return record.levelno == self.level

def setup_logger(handler_name):
    """
    Create and return a logger with handlers for console, debug, info, and error logs.
    Prevents adding handlers multiple times.
    """
    #print(f"Initializing logger1: {handler_name}")
    logger = logging.getLogger(handler_name)

    #Prevent adding handlers multiple times
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(logging.DEBUG)  # Capture all levels

    # Ensure log folder and files exist
    os.makedirs(LOG_FOLDER, exist_ok=True)

    # Common formatter for all handlers
    formatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s')

    log_levels = [
        (DEBUG_LOG_PATH, logging.DEBUG),
        (INFO_LOG_PATH, logging.INFO),
        (ERROR_LOG_PATH, logging.ERROR),
    ]

    for filepath, level in log_levels:
        handler = RotatingFileHandler(
            filename=filepath,
            maxBytes=10*1024*1024,  # 10MB per file
            backupCount=5
        )
        handler.setLevel(level)
        handler.setFormatter(formatter)

        handler.addFilter(LevelFilter(level))

        logger.addHandler(handler)

    # Console handler for real-time output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


if __name__ == "__main__":
    logger = setup_logger("netpilot_logger")
    logger.info("Logger initialized successfully.")
    logger.debug("This is a debug message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")
    logger.warning("This is a warning message.")
