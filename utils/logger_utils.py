
import logging
import os
from scripts.constants import (
    DEBUG_LOG_PATH,
    INFO_LOG_PATH,
    ERROR_LOG_PATH,
    LOG_FOLDER,
)


# -----------------------------------------------------------------------------
def logger_handler(handler_name):
    """
    Logger setup for the backup manager.
    Creates a logger with handlers for console, debug, info, and error logs.
    """

    # Ensure the log directory and files exist
    os.makedirs(LOG_FOLDER, exist_ok=True)

    if not os.path.exists(ERROR_LOG_PATH):
        with open(ERROR_LOG_PATH, 'w') as f:
            f.write("Error log initialized.\n")
    if not os.path.exists(INFO_LOG_PATH):
        with open(INFO_LOG_PATH, 'w') as f:
            f.write("Info log initialized.\n")
    if not os.path.exists(DEBUG_LOG_PATH):
        with open(DEBUG_LOG_PATH, 'w') as f:
            f.write("Debug log initialized.\n")

    # Logger initialization
    logger = logging.getLogger(handler_name)
    logger.setLevel(logging.DEBUG)  # Adjust according to the use case

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    # File handlers for different log levels
    debug_handler = logging.FileHandler(DEBUG_LOG_PATH)
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s'))

    info_handler = logging.FileHandler(INFO_LOG_PATH)
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s'))

    error_handler = logging.FileHandler(ERROR_LOG_PATH)
    error_handler.setLevel(logging.WARNING)
    error_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s'))

    # Console handler for real-time messages
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)  # Shows DEBUG+ logs on console
    console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s'))

    # Add handlers to logger
    logger.addHandler(debug_handler)
    logger.addHandler(info_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)
    
    return logger


# -----------------------------------------------------------------------------
def log_error(output):
    """
    Function to add logs to a file with a timestamp.
    Args:
        error_output (str): The error message to log.
    """

    error_output = str(output).strip()
    if not error_output:
        return  # If the output is empty, do not log anything

    # Ensure the log directory exists
    import os
    if not os.path.exists(LOG_FOLDER):
        os.makedirs(LOG_FOLDER)
    # Write the error message to the log file with a timestamp

    from datetime import datetime
    error_line = '{} {}\n'.format(str(datetime.now()), error_output)
    with open(ERROR_LOG_PATH, "a") as file:
        file.write(error_line)
    print(error_line, end='')  # Print to console as well


# -----------------------------------------------------------------------------
def log_info(output):
    """
    Function to add logs to a file with a timestamp.
    Args:
        output (str): The message to log.
    """ 
    
    output = str(output).strip()
    if not output:
        return  # If the output is empty, do not log anything

    # Ensure the log directory exists
    import os
    if not os.path.exists(LOG_FOLDER):
        os.makedirs(LOG_FOLDER)
    # Write the message to the log file with a timestamp

    from datetime import datetime
    info_line = '{} {}\n'.format(str(datetime.now()), output)
    with open(INFO_LOG_PATH, "a") as file:
        file.write(info_line)
    print(info_line, end='')  # Print to console as well


# -----------------------------------------------------------------------------
def log_debug(output):
    """
    Function to add debug logs to a file with a timestamp.
    Args:
        output (str): The debug message to log.
    """

    output = str(output).strip()
    if not output:
        return  # If the output is empty, do not log anything

    # Ensure the log directory exists
    import os
    if not os.path.exists(LOG_FOLDER):
        os.makedirs(LOG_FOLDER)
    # Write the debug message to the log file with a timestamp

    from datetime import datetime
    debug_line = '{} {}\n'.format(str(datetime.now()), output)
    with open(DEBUG_LOG_PATH, "a") as file:
        file.write(debug_line)
    print(debug_line, end='')  # Print to console as well



if __name__ == "__main__":
    
    # Example usage of the logging functions
    log_info("This is an informational message.")
    log_error("This is an error message.")
    log_debug("This is a debug message.")
