# inventory_manager.py
# -*- coding: utf-8 -*-
# This file is part of the Network Automation Suite.

import os
import yaml
from concurrent.futures import ThreadPoolExecutor, as_completed

from scripts.constants import (
    DEVICES_FILE_PATH,
    CONFIG_FILE_PATH,
    GROUP_TO_DEVICE_TYPE,
    INVENTORY_FOLDER_PATH,
    INVENTORY_RESULT_FILE_PATH,
)
from scripts.netmiko_utils import get_device_inventory
from scripts.config_parser import load_yaml
from utils.network_utils import validate_ip, is_reachable
from utils.logger_utils import setup_logger

logger = setup_logger("inventory_manager")
#logger.info("Inventory task started -- 2")

def inventory_task(device, device_type):
    """Collect inventory from a single device, log result and return status."""
    ip = device.get("host")
    device_name = device.get("name", "UNKNOWN")
    logger.info(f"Starting inventory collection for {device_name}")

    result = {
        "device": device_name,
        "host": ip,
        "status": "FAILED",
        "output": ""
    }

    if not validate_ip(ip):
        msg = f"Invalid IP address for device {device_name}: {ip}"
        logger.error(msg)
        result["output"] = msg
        return result

    if not is_reachable(ip):
        msg = f"Device not reachable for device {device_name}: {ip}"
        logger.error(msg)
        result["output"] = msg
        return result

    try:
        inventory = get_device_inventory(device, device_type)
        result["status"] = "SUCCESS"
        result["output"] = inventory
        logger.info(f"Inventory SUCCESS: {device_name} ({ip})")
    except Exception as e:
        result["output"] = str(e)
        logger.error(f"Inventory FAILED: {device_name} ({ip}): {e}")

    return result

def main():
    """Main entry for inventory collection using multithreading."""
    config = load_yaml(CONFIG_FILE_PATH)
    thread_params = config.get("thread_pools", {})
    num_threads = thread_params.get("num_threads", 5)

    devices_yaml = load_yaml(DEVICES_FILE_PATH)
    devices = devices_yaml.get("devices", [])
    if not devices:
        logger.error("No devices found for inventory collection.")
        return

    #logger.info("Inventory task started -- 3")
    os.makedirs(INVENTORY_FOLDER_PATH, exist_ok=True)
    results = []
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [
            executor.submit(inventory_task, device, GROUP_TO_DEVICE_TYPE.get(device.get("group")))
            for device in devices if GROUP_TO_DEVICE_TYPE.get(device.get("group"))
        ]
        for future in as_completed(futures):
            results.append(future.result())
        #logger.info("Inventory task started -- 4")

    with open(INVENTORY_RESULT_FILE_PATH, "w") as f:
        yaml.dump(results, f, default_flow_style=False, allow_unicode=True)
    logger.info(f"Inventory results written to {INVENTORY_RESULT_FILE_PATH}")

if __name__ == "__main__":
    main()
