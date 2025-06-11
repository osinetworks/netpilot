
import logging
import os
from scripts.constants import (
    DEBUG_LOG_PATH,
    INFO_LOG_PATH,
    ERROR_LOG_PATH,
)

def logger_handler(handler_name):
    """
    Logger setup for the backup manager.
    Creates a logger with handlers for console, debug, info, and error logs.
    """

    # -----------------------------------------------------------------------------
    # --- Create logs directory if it doesn't exist ---
    os.makedirs("logs", exist_ok=True)

    # --- Logger Setup ---
    logger = logging.getLogger(handler_name)
    logger.setLevel(logging.DEBUG)

    if logger.hasHandlers():
        logger.handlers.clear()

    # console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s'))

    # debug, info, and error handlers
    debug_handler = logging.FileHandler(DEBUG_LOG_PATH)
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s'))

    info_handler = logging.FileHandler(INFO_LOG_PATH)
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s'))

    error_handler = logging.FileHandler(ERROR_LOG_PATH)
    error_handler.setLevel(logging.WARNING)
    error_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s'))

    logger.addHandler(console_handler)
    logger.addHandler(debug_handler)
    logger.addHandler(info_handler)
    logger.addHandler(error_handler)

    # --- End Logger Setup ---
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
    if not os.path.exists("log"):
        os.makedirs("log")
    # Write the error message to the log file with a timestamp

    from datetime import datetime
    error_line = '{} {}\n'.format(str(datetime.now()), error_output)
    with open("log/error.log", "a") as file:
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
    if not os.path.exists("log"):
        os.makedirs("log")
    # Write the message to the log file with a timestamp

    from datetime import datetime
    info_line = '{} {}\n'.format(str(datetime.now()), output)
    with open("log/info.log", "a") as file:
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
    if not os.path.exists("log"):
        os.makedirs("log")
    # Write the debug message to the log file with a timestamp

    from datetime import datetime
    debug_line = '{} {}\n'.format(str(datetime.now()), output)
    with open("log/debug.log", "a") as file:
        file.write(debug_line)
    print(debug_line, end='')  # Print to console as well



if __name__ == "__main__":
    
    # Example usage of the logging functions
    log_info("This is an informational message.")
    log_error("This is an error message.")
    log_debug("This is a debug message.")
