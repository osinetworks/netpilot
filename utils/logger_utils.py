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
    

def parse_log(log_entry):
    """
    Parse a simple log entry string into a structured dictionary.
    "2025-06-21 18:00:37 | ERROR | [config_manager] | Device unreachable (port 22) for cisco-sw-003| 10.10.10.13"
    """
    # Split the log entry by '|'
    parts = log_entry.split('|')
    
    if len(parts) == 5:
        timestamp = parts[0].strip()                # timestamp
        error_level = parts[1].strip()              # error level
        function = parts[2].strip().strip('[]')     # function that produced the error
        error_message = parts[3].strip()            # error message
        ip_address = parts[4].strip()               # IP address

        return {
            'timestamp': timestamp,
            'error_level': error_level,
            'function': function,
            'error_message': error_message,
            'ip_address': ip_address
        }
    else:
        return None


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

    # Sample format: 2025-06-21 18:10:32
    date_format = "%Y-%m-%d %H:%M:%S"
    log_format = "%(asctime)s | %(levelname)s | [%(name)s] | %(message)s"

    # Common formatter for all handlers
    formatter = logging.Formatter(log_format, datefmt=date_format)

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
