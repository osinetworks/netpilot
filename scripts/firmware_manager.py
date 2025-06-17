# firmware_manager.py

import os
import yaml
from filelock import FileLock
from concurrent.futures import ThreadPoolExecutor, as_completed

from scripts.constants import (
    DEVICES_FILE_PATH,
    CONFIG_FILE_PATH,
    GROUP_TO_DEVICE_TYPE,
    OUTPUT_FOLDER,
    FIRMWARE_RESULT_FILE_PATH,
)

from scripts.netmiko_utils import firmware_upgrade_procedure
from scripts.worker import device_worker
from scripts.config_parser import load_yaml
from utils.network_utils import validate_devices, validate_ip, is_reachable

from utils.logger_utils import setup_logger

# --- Logger Setup ---
logger = setup_logger("firmware_manager")

def firmware_task(device, device_type):
    """
    Task to upgrade firmware on a single device.
    Returns a result dict.
    """
    logger.info(f"Starting firmware upgrade for {device.get('name')}")
    result = {
        "device": device.get("name", "UNKNOWN"),
        "host": device.get("host", "UNKNOWN"),
        "status": "FAILED",
        "output": ""
    }
    ip = device.get("host")
    if not validate_ip(ip):
        msg = f"Invalid IP address: {ip}"
        result["output"] = msg
        logger.error(msg)
        return result

    try:
        output = firmware_upgrade_procedure(device, device_type)
        result["status"] = "SUCCESS"
        result["output"] = output
        logger.info(f"Firmware upgrade SUCCESS: {result['device']} ({ip})")
    except Exception as e:
        result["output"] = str(e)
        msg = f"Firmware upgrade FAILED: {result['device']} ({ip}): {e}"
        logger.error(msg)
    return result

def main():
    """
    Main function to handle firmware upgrade tasks.
    """
    config = load_yaml(CONFIG_FILE_PATH)
    thread_params = config.get("thread_pools", {})
    num_threads = thread_params.get("num_threads", 5)

    devices_yaml = load_yaml(DEVICES_FILE_PATH)
    devices = devices_yaml.get("devices", [])

    if not devices:
        logger.error("No devices found for firmware upgrade.")
        return [], True

    results = []
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for device in devices:
            group = device.get("group")
            device_type = GROUP_TO_DEVICE_TYPE.get(group)
            if not device_type:
                msg = f"Unknown group '{group}' for device {device['name']}"
                logger.error(msg)
                continue
            futures.append(executor.submit(firmware_task, device, device_type))

        for future in as_completed(futures):
            results.append(future.result())

    # Write results as YAML
    output_file = FIRMWARE_RESULT_FILE_PATH
    lock_file = f"{output_file}.lock"
    lock = FileLock(lock_file)
    with lock:
        with open(output_file, "w") as f:
            yaml.dump(results, f, default_flow_style=False, allow_unicode=True)
        logger.info(f"Firmware upgrade results written to {output_file}")

    if os.path.exists(lock_file):
        os.remove(lock_file)


if __name__ == "__main__":
    main()
