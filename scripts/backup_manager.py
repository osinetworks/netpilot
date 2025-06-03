import os
import yaml
import logging

# --- LOG HANDLER SETUP (EKLENDİ) ---
os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("backup_manager")
logger.setLevel(logging.DEBUG)  # DEBUG ile tüm seviyeler loglanır

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
# --- LOG HANDLER SETUP SONU ---

from concurrent.futures import ThreadPoolExecutor, as_completed
from scripts.constants import (
    DEVICES_FILE_PATH,
    GROUP_TO_DEVICE_TYPE,
    BACKUP_FOLDER_PATH,
    BACKUP_RESULT_FILE_PATH,
    DEVICES_FILE_PATH,
    GROUP_TO_DEVICE_TYPE,
)

from scripts.netmiko_utils import backup_device_config
from scripts.worker import device_worker
from scripts.config_parser import load_yaml
from utils.network_utils import validate_ip

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
        logger.error(f"Backup FAILED: {result['device']} ({ip}): {e}")
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
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for device in devices:
            group = device.get("group")
            device_type = GROUP_TO_DEVICE_TYPE.get(group)
            if not device_type:
                logger.error(f"Unknown group '{group}' for device {device['name']}")
                continue
           #futures.append(executor.submit(backup_task, device, device_type))
            executor.submit(device_worker, backup_task, device, device_type)

        for future in as_completed(futures):
            results.append(future.result())

    # Write results as YAML
    output_file = BACKUP_RESULT_FILE_PATH
    with open(output_file, "w") as f:
        yaml.dump(results, f, default_flow_style=False, allow_unicode=True)
    logger.info(f"Backup results written to {output_file}")


if __name__ == "__main__":
    main()
