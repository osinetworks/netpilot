# logger_utils.py

import logging
import os
from datetime import datetime
from scripts.constants import (
    DEBUG_LOG_PATH,
    INFO_LOG_PATH,
    ERROR_LOG_PATH,
    LOG_FOLDER,
)

def setup_logger(handler_name):
    """
    Create and return a logger with handlers for console, debug, info, and error logs.
    Prevents adding handlers multiple times.
    """
    #print(f"Initializing logger1: {handler_name}")
    logger = logging.getLogger(handler_name)
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.setLevel(logging.DEBUG)  # Capture all levels

    # Ensure log folder and files exist
    os.makedirs(LOG_FOLDER, exist_ok=True)
    for log_path, init_msg in [
        (ERROR_LOG_PATH, "Error log initialized.\n"),
        (INFO_LOG_PATH, "Info log initialized.\n"),
        (DEBUG_LOG_PATH, "Debug log initialized.\n"),
    ]:
        if not os.path.exists(log_path):
            with open(log_path, 'w') as f:
                f.write(init_msg)

    # File handlers
    debug_handler = logging.FileHandler(DEBUG_LOG_PATH)
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s'))
    logger.addHandler(debug_handler)

    info_handler = logging.FileHandler(INFO_LOG_PATH)
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s'))
    logger.addHandler(info_handler)

    warning_handler = logging.FileHandler(ERROR_LOG_PATH)
    warning_handler.setLevel(logging.WARNING)
    warning_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s'))
    logger.addHandler(warning_handler)

    error_handler = logging.FileHandler(ERROR_LOG_PATH)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s'))
    logger.addHandler(error_handler)

    # Console handler for real-time output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s'))
    logger.addHandler(console_handler)

    return logger

def log_error(output):
    """
    Write an error message to the error log file and print it to the console.
    """
    output = str(output).strip()
    if not output:
        return
    os.makedirs(LOG_FOLDER, exist_ok=True)
    error_line = '{} {}\n'.format(str(datetime.now()), output)
    with open(ERROR_LOG_PATH, "a") as file:
        file.write(error_line)
    print(error_line, end='')

def log_info(output):
    """
    Write an info message to the info log file and print it to the console.
    """
    output = str(output).strip()
    if not output:
        return
    os.makedirs(LOG_FOLDER, exist_ok=True)
    info_line = '{} {}\n'.format(str(datetime.now()), output)
    with open(INFO_LOG_PATH, "a") as file:
        file.write(info_line)
    print(info_line, end='')

def log_debug(output):
    """
    Write a debug message to the debug log file and print it to the console.
    """
    output = str(output).strip()
    if not output:
        return
    os.makedirs(LOG_FOLDER, exist_ok=True)
    debug_line = '{} {}\n'.format(str(datetime.now()), output)
    with open(DEBUG_LOG_PATH, "a") as file:
        file.write(debug_line)
    print(debug_line, end='')

if __name__ == "__main__":
    # Example usage of the logging functions
    log_info("This is an informational message.")
    log_error("This is an error message.")
    log_debug("This is a debug message.")
