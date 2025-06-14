# inventory_manager.py

import os
import yaml
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from scripts.constants import (
    DEVICES_FILE_PATH,
    CONFIG_FILE_PATH,
    GROUP_TO_DEVICE_TYPE,
    OUTPUT_FOLDER,
    ERROR_LOG_PATH,
)
from scripts.netmiko_utils import get_device_inventory
from scripts.worker import device_worker
from scripts.config_parser import load_yaml
from utils.network_utils import validate_ip

logger = logging.getLogger("inventory_manager")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s'))
logger.addHandler(console_handler)

error_logger = logging.getLogger("inventory_error_logger")
error_logger.setLevel(logging.ERROR)
error_handler = logging.FileHandler(ERROR_LOG_PATH)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s'))
if not error_logger.hasHandlers():
    error_logger.addHandler(error_handler)


def inventory_task(device, device_type):
    """
    Task to collect inventory information from a device.
    """
    result = {
        "device": device.get("name", "UNKNOWN"),
        "host": device.get("host", "UNKNOWN"),
        "status": "FAILED",
        "output": ""
    }
    ip = device.get("host")
    if not validate_ip(ip):
        result["output"] = f"Invalid IP address: {ip}"
        msg = f"Invalid IP address for device {result['device']}: {ip}"
        logger.error(msg)
        error_logger.error(msg)
        return result
    try:
        inventory = get_device_inventory(device, device_type)
        result["status"] = "SUCCESS"
        result["output"] = inventory
        logger.info(f"Inventory SUCCESS: {result['device']} ({ip})")
    except Exception as e:
        result["output"] = str(e)
        msg = f"Inventory FAILED: {result['device']} ({ip}): {e}"
        logger.error(msg)
        error_logger.error(msg)
    return result


def main():
    # Thread numbers and device groups are loaded from YAML config files
    config = load_yaml(CONFIG_FILE_PATH)
    thread_params = config.get("thread_pools", {})
    num_threads = thread_params.get("num_threads", 5)

    devices_yaml = load_yaml(DEVICES_FILE_PATH)
    devices = devices_yaml.get("devices", [])
    if not devices:
        logger.critical("No devices found for inventory collection.")
        return

    results = []
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for device in devices:
            group = device.get("group")
            device_type = GROUP_TO_DEVICE_TYPE.get(group)
            if not device_type:
                logger.error(f"Unknown group '{group}' for device {device['name']}")
                continue

            future = executor.submit(device_worker, inventory_task, device, device_type)
            futures.append(future)
            
        for future in as_completed(futures):
            results.append(future.result())

    output_dir = os.path.join(OUTPUT_FOLDER, "inventory")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "inventory_results.yaml")
    with open(output_file, "w") as f:
        yaml.dump(results, f, default_flow_style=False, allow_unicode=True)
    logger.info(f"Inventory results written to {output_file}")

if __name__ == "__main__":
    main()
