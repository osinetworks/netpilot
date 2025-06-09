import os
import yaml
import logging

from concurrent.futures import ThreadPoolExecutor, as_completed
from scripts.constants import (
    DEVICES_FILE_PATH,
    GROUP_TO_DEVICE_TYPE,
    BACKUP_FOLDER_PATH,
    ERROR_LOG_PATH,
)

from scripts.netmiko_utils import backup_device_config
from scripts.worker import device_worker
from scripts.config_parser import load_yaml
from utils.network_utils import validate_ip

# --- LOG HANDLER SETUP (EKLENDİ) ---
os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("backup_manager")
logger.setLevel(logging.DEBUG) # Set to DEBUG to capture all logs

# Console Handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s'))
logger.addHandler(console_handler)

# File Handler (Debug)
file_handler = logging.FileHandler('logs/debug.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s'))
logger.addHandler(file_handler)


error_logger = logging.getLogger("backup_error_logger")
error_logger.setLevel(logging.ERROR)
error_handler = logging.FileHandler(ERROR_LOG_PATH)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s'))
if not error_logger.hasHandlers():
    error_logger.addHandler(error_handler)

# --- END OF LOG HANDLER SETUP ---

logger = logging.getLogger("backup_manager")
logger.setLevel(logging.INFO)


def backup_task(device, device_type):
    """Backup running and startup config from a single device."""

    logger.info(f"Starting backup for {device.get('name')}")

    result = {
        "device": device.get("name", "UNKNOWN"),
        "host": device.get("host", "UNKNOWN"),
        "status": "FAILED",
        "files": [],
        "output": ""
    }
    ip = device.get("host")
    if not validate_ip(ip):
        msg = f"Invalid IP address: {ip}"
        result["output"] = msg
        logger.error(msg)
        return result

    try:
        files, output = backup_device_config(device, device_type)
        result["status"] = "SUCCESS"
        result["files"] = files
        result["output"] = output
        logger.info(f"Backup SUCCESS: {result['device']} ({ip}) Files: {files}")
    except Exception as e:
        result["output"] = str(e)
        msg = f"Backup FAILED: {result['device']} ({ip}): {e}"
        logger.error(msg)
        error_logger.error(msg)

    return result


def main():
    """Main function to handle backup tasks."""

    devices_yaml = load_yaml(DEVICES_FILE_PATH)
    devices = devices_yaml.get("devices", [])

    if not devices:
        logger.critical("No devices found for backup.")
        return

    os.makedirs(BACKUP_FOLDER_PATH, exist_ok=True)

    results = []
    any_failed = False
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for device in devices:
            group = device.get("group")
            device_type = GROUP_TO_DEVICE_TYPE.get(group)
            if not device_type:
                logger.error(f"Unknown group '{group}' for device {device['name']}")
                error_logger.error(f"Unknown group '{group}' for device {device['name']}")
                continue
            futures.append(executor.submit(backup_task, device, device_type))

        for future in as_completed(futures):
            res = future.result()
            results.append(res)
            if res.get("status") != "SUCCESS":
                any_failed = True

    # Write results as YAML
    output_file = os.path.join(BACKUP_FOLDER_PATH, "backup_results.yaml")
    with open(output_file, "w") as f:
        yaml.dump(results, f, default_flow_style=False, allow_unicode=True)
    logger.info(f"Backup results written to {output_file}")

    # Return results and status
    return results, any_failed


if __name__ == "__main__":
    main()
