# firmware_manager.py

import os
import yaml
import logging
from scripts.constants import (
    DEVICES_FILE_PATH,
    CONFIG_FILE_PATH,
    GROUP_TO_DEVICE_TYPE,
    OUTPUT_FOLDER,
    ERROR_LOG_PATH,
)
from scripts.netmiko_utils import firmware_upgrade_procedure
from scripts.worker import device_worker
from scripts.config_parser import load_yaml
from utils.network_utils import validate_ip
from concurrent.futures import ThreadPoolExecutor, as_completed


# --- LOG HANDLER SETUP ---
os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("firmware_manager")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s'))
logger.addHandler(console_handler)

file_handler = logging.FileHandler('logs/debug.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s'))
logger.addHandler(file_handler)

error_logger = logging.getLogger("firmware_error_logger")
error_logger.setLevel(logging.ERROR)
error_handler = logging.FileHandler(ERROR_LOG_PATH)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s'))
if not error_logger.hasHandlers():
    error_logger.addHandler(error_handler)
# --- END LOG HANDLER SETUP ---

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
        error_logger.error(msg)
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
        error_logger.error(msg)
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
        logger.critical("No devices found for firmware upgrade.")
        return [], True

    results = []
    any_failed = False
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for device in devices:
            group = device.get("group")
            device_type = GROUP_TO_DEVICE_TYPE.get(group)
            if not device_type:
                msg = f"Unknown group '{group}' for device {device['name']}"
                logger.error(msg)
                error_logger.error(msg)
                continue
            futures.append(executor.submit(firmware_task, device, device_type))

        for future in as_completed(futures):
            res = future.result()
            results.append(res)
            if res.get("status") != "SUCCESS":
                any_failed = True

    # Save results to YAML
    output_dir = os.path.join(OUTPUT_FOLDER, "firmware")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "firmware_results.yaml")
    with open(output_file, "w") as f:
        yaml.dump(results, f, default_flow_style=False, allow_unicode=True)

    if any_failed:
        logger.warning("Some devices failed firmware upgrade! See error.log for details.")
        print("Some devices failed firmware upgrade! See error.log for details.")
    else:
        logger.info("Firmware upgrade completed successfully!")
        print("Firmware upgrade completed successfully!")
    return results, any_failed


if __name__ == "__main__":
    main()
