
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
