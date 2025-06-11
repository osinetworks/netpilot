# backup_manager.py
# -*- coding: utf-8 -*-
# This file is part of the Network Automation Suite.

import os
import yaml
from filelock import FileLock
from concurrent.futures import ThreadPoolExecutor, as_completed

from scripts.constants import (
    DEVICES_FILE_PATH,
    GROUP_TO_DEVICE_TYPE,
    BACKUP_FOLDER_PATH,
    BACKUP_RESULT_FILE_PATH,
    CONFIG_FILE_PATH,
)

from scripts.netmiko_utils import backup_device_config
from scripts.worker import device_worker
from scripts.config_parser import load_yaml
from utils.network_utils import validate_devices, validate_ip, is_reachable
from utils.logger_utils import logger_handler

# --- Logger Setup ---
logger = logger_handler("backup_manager")


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

    return result


def main():
    """Main function to handle backup tasks."""

    config = load_yaml(CONFIG_FILE_PATH)
    thread_params = config.get("thread_pools", {})
    num_threads = thread_params.get("num_threads", 5)

    devices_yaml = load_yaml(DEVICES_FILE_PATH)
    devices = devices_yaml.get("devices", [])

    devices = validate_devices(devices, logger)
    if not devices:
        logger.error("No devices found for backup.")
        return

    os.makedirs(BACKUP_FOLDER_PATH, exist_ok=True)

    results = []
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for device in devices:
            group = device.get("group")
            device_type = GROUP_TO_DEVICE_TYPE.get(group)
            if not device_type:
                logger.error(f"Unknown group '{group}' for device {device['name']}")
                continue
            futures.append(executor.submit(backup_task, device, device_type))
        
        for future in as_completed(futures):
            results.append(future.result())

    # Write results as YAML
    output_file = BACKUP_RESULT_FILE_PATH
    lock_file = f"{output_file}.lock"
    lock = FileLock(lock_file)
    with lock:
        with open(output_file, "w") as f:
            yaml.dump(results, f, default_flow_style=False, allow_unicode=True)
        logger.info(f"Backup results written to {output_file}")

    if os.path.exists(lock_file):
        os.remove(lock_file)
        

if __name__ == "__main__":
    main()
