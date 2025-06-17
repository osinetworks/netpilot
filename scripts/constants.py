import os

# Set environment profile: "development", "test", "production"
ENVIRONMENT = os.getenv("NETAUTO_ENV", "production")

# Config file path
CONFIG_FILE_PATH = os.path.join("config", "config.yaml")

# Devices YAML file path
DEVICES_FILE_PATH = os.path.join("config", "devices.yaml")

# Credentials file path
CREDENTIALS_FILE_PATH = os.path.join("config", "credentials.yaml")

# Devices YAML file path
DEVICES_FILE_PATH = os.path.join("config", "devices.yaml")

# Firmware config file path
FIRMWARE_CONFIG_PATH = os.path.join("config", "firmware.yaml")

# config commands folder path
COMMANDS_FOLDER_PATH = os.path.join("config", "commands")

# Command file paths
CONFIG_COMMANDS_FILE = {
    "arista_eos": "arista_eos_config_commands.cfg",
    "cisco_ios": "cisco_ios_config_commands.cfg",
}

# Command file paths for different device types
CONFIG_COMMANDS_PATHS = {
    "arista_eos": os.path.join(COMMANDS_FOLDER_PATH, CONFIG_COMMANDS_FILE["arista_eos"]),
    "cisco_ios": os.path.join(COMMANDS_FOLDER_PATH, CONFIG_COMMANDS_FILE["cisco_ios"]),
}

# Output folder path
OUTPUT_FOLDER = "output/"

# Output file path for config results
CONFIG_RESULT_FILE_PATH = os.path.join(OUTPUT_FOLDER, "config", "config_results.yaml")

# BACKUP file paths
BACKUP_COMMANDS_FILE = {
    "arista_eos": "arista_backup_commands.cfg",
    "cisco_ios": "cisco_ios_backup_commands.cfg",
}

# Backup command file paths
BACKUP_COMMANDS_PATHS = {
    "arista_eos": os.path.join(COMMANDS_FOLDER_PATH, BACKUP_COMMANDS_FILE["arista_eos"]),
    "cisco_ios": os.path.join(COMMANDS_FOLDER_PATH, BACKUP_COMMANDS_FILE["cisco_ios"]),
}

# Backup folder path
BACKUP_FOLDER_PATH = os.path.join(OUTPUT_FOLDER, "backup")

# Output file path for config results
BACKUP_RESULT_FILE_PATH = os.path.join(BACKUP_FOLDER_PATH, "backup_results.yaml")

# Inventory folder path
INVENTORY_FOLDER_PATH = os.path.join(OUTPUT_FOLDER, "inventory")

# Output file path for inventory results
INVENTORY_RESULT_FILE_PATH = os.path.join(INVENTORY_FOLDER_PATH, "inventory_results.yaml")

# Inventory command file paths
INVENTORY_COMMANDS_FILE = {
    "arista_eos": "arista_eos_inventory_commands.cfg",
    "cisco_ios": "cisco_ios_inventory_commands.cfg",
}

# Inventory command file paths for different device types
INVENTORY_COMMANDS_PATHS = {
    "arista_eos": os.path.join(COMMANDS_FOLDER_PATH, INVENTORY_COMMANDS_FILE["arista_eos"]),
    "cisco_ios": os.path.join(COMMANDS_FOLDER_PATH, INVENTORY_COMMANDS_FILE["cisco_ios"]),
}

# Firmware update folder path
FIRMWARE_FOLDER = "firmware/"

# Output file path for firmware results
FIRMWARE_RESULT_FILE_PATH = os.path.join(FIRMWARE_FOLDER, "firmware_results.yaml")

# Log folder path
LOG_FOLDER = "logs/"

# Error Log path
ERROR_LOG_PATH = os.path.join(LOG_FOLDER, "error.log")

# Info Log path
INFO_LOG_PATH = os.path.join(LOG_FOLDER, "info.log")

# Debug Log path
DEBUG_LOG_PATH = os.path.join(LOG_FOLDER, "debug.log")

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


CONFIG_BUTTON = "Run Config Task"
BACKUP_BUTTON = "Run Backup Task"
INVENTORY_BUTTON = "Run Inventory Task"
FIRMWARE_BUTTON = "Run Firmware Task"
CLEAR_LOGS_BUTTON = "Clear Log"
SHOW_ERRORS_BUTTON = "Show Error Logs"

# Default device IP. Change this to the IP of your device. This is used for testing purposes.
DEFAULT_DEVICE_IP = "172.20.20.101"
