# utils/exceptions.py

class ConfigFileError(Exception):
    """Raised when there is a YAML/config file error."""
    pass

class DeviceConnectionError(Exception):
    """Raised when a device is unreachable or SSH fails."""
    pass

class InventoryParseError(Exception):
    """Raised when there is an error parsing inventory data."""
    pass

# Can be added more exceptions:  CommandExecutionError, BackupError, etc.
