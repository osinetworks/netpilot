import os

# Set environment profile: "development", "test", "production"
ENVIRONMENT = os.getenv("NETAUTO_ENV", "production")

# Config file path
CONFIG_FILE_PATH = "config/config.yaml"

# Devices YAML file path
DEVICES_FILE_PATH = "config/devices.yaml"

# Credentials file path
CREDENTIALS_FILE_PATH = "config/credentials.yaml"

# Output folder path
OUTPUT_FOLDER = "output/"

# Output file path for config results
CONFIG_RESULT_FILE_PATH = os.path.join(OUTPUT_FOLDER, "config", "config_results.yaml")

# Backup folder path
BACKUP_FOLDER_PATH = os.path.join(OUTPUT_FOLDER, "backup")

# Output file path for config results
BACKUP_RESULT_FILE_PATH = os.path.join(BACKUP_FOLDER_PATH, "backup_results.yaml")

# Devices YAML file path
DEVICES_FILE_PATH = "config/devices.yaml"

# Firmware config file path
FIRMWARE_CONFIG_PATH = "config/firmware.yaml"

# Log folder path
LOG_FOLDER = "logs/"

# Error Log path
ERROR_LOG_PATH = os.path.join(LOG_FOLDER, "error.log")

# Info Log path
INFO_LOG_PATH = os.path.join(LOG_FOLDER, "info.log")

# Debug Log path
DEBUG_LOG_PATH = os.path.join(LOG_FOLDER, "debug.log")

# Firmware update folder path
FIRMWARE_FOLDER = "firmware/"

# Command file paths
COMMANDS_PATHS = {
    "arista_eos": "config/commands/arista_config_commands.cfg",
    "cisco_ios": "config/commands/cisco_config_commands.cfg",
}

# Inventory command file paths
INVENTORY_COMMANDS_PATHS = {
    "arista_eos": "config/commands/arista_inventory_commands.cfg",
    "cisco_ios": "config/commands/cisco_inventory_commands.cfg",
}

# Backup command file paths
BACKUP_COMMANDS_PATHS = {
    "arista_eos": "config/commands/arista_backup_commands.cfg",
    "cisco_ios": "config/commands/cisco_backup_commands.cfg",
}

# Group to device_type mapping
GROUP_TO_DEVICE_TYPE = {
    "arista": "arista_eos",
    "cisco": "cisco_ios"
}

# Supported device types
SUPPORTED_DEVICE_TYPES = [
    "cisco_ios",
    "arista_eos",
]

# Supported tasks
SUPPORTED_TASKS = [
    "config",
    "backup",
    "inventory",
    "firmware",
]

# Default device IP. Change this to the IP of your device. This is used for testing purposes.
DEFAULT_DEVICE_IP = "172.20.20.101"
