# inventory_manager.py
# -*- coding: utf-8 -*-
# This file is part of the Network Automation Suite.

import os
import yaml
import logging
from filelock import FileLock

from concurrent.futures import ThreadPoolExecutor, as_completed
from scripts.constants import (
    DEVICES_FILE_PATH,
    CONFIG_FILE_PATH,
    GROUP_TO_DEVICE_TYPE,
    OUTPUT_FOLDER,
    INVENTORY_FOLDER_PATH,
    INVENTORY_RESULT_FILE_PATH,
)
from scripts.netmiko_utils import get_device_inventory
from scripts.worker import device_worker
from scripts.config_parser import load_yaml
from utils.network_utils import validate_ip, validate_devices, is_reachable
from utils.logger_utils import logger_handler

# --- Logger Setup ---
logger = logging.getLogger("inventory_manager")


def inventory_task(device, device_type):
    """
    Task to collect inventory information from a device.
    """

    logger.info(f"Starting inventory collection for {device.get('name')}")
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

    return result


def main():
    ''' Thread numbers and device groups are loaded from YAML config files '''

    config = load_yaml(CONFIG_FILE_PATH)
    thread_params = config.get("thread_pools", {})
    num_threads = thread_params.get("num_threads", 5)

    devices_yaml = load_yaml(DEVICES_FILE_PATH)
    devices = devices_yaml.get("devices", [])
    
    devices = validate_devices(devices, logger)
    if not devices:
        logger.error("No devices found for inventory collection.")
        return

    os.makedirs(INVENTORY_FOLDER_PATH, exist_ok=True)

    results = []
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for device in devices:
            group = device.get("group")
            device_type = GROUP_TO_DEVICE_TYPE.get(group)
            if not device_type:
                logger.error(f"Unknown group '{group}' for device {device['name']}")
                continue
            futures.append(executor.submit(inventory_task, device, device_type))
            
        for future in as_completed(futures):
            results.append(future.result())

    # Write results as YAML
    output_file = INVENTORY_RESULT_FILE_PATH
    lock_file = f"{output_file}.lock"
    lock = FileLock(lock_file)
    with lock:
        with open(output_file, "w") as f:
            yaml.dump(results, f, default_flow_style=False, allow_unicode=True)
        logger.info(f"Inventory results written to {output_file}")

    if os.path.exists(lock_file):
        os.remove(lock_file)


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
