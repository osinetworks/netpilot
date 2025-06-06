import os
import yaml
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from scripts.constants import (
    DEVICES_FILE_PATH,
    CONFIG_FILE_PATH,
    GROUP_TO_DEVICE_TYPE,
    OUTPUT_FOLDER,
    INVENTORY_RESULT_FILE_PATH,
    ERROR_LOG_PATH,
)
from scripts.netmiko_utils import get_device_inventory
from scripts.config_parser import load_yaml
from utils.network_utils import validate_ip

logger = logging.getLogger("inventory_manager")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s'))
logger.addHandler(console_handler)

# Separate error logger for error.log
error_logger = logging.getLogger("inventory_error_logger")
error_handler = logging.FileHandler(ERROR_LOG_PATH)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s'))
error_logger.addHandler(error_handler)

def parse_arista_inventory(output):
    """
    Parse Arista 'show inventory' output to extract model and SFP count.
    """
    lines = output.splitlines()
    model = None
    sfp_count = 0
    for line in lines:
        if "Model" in line and not model:
            parts = line.split()
            if len(parts) > 1:
                model = parts[-1]
        if "SwitchedBootstrap" in line or "SFP" in line:
            try:
                sfp_count += int(line.strip().split()[-1])
            except Exception:
                continue
    return model, sfp_count

def parse_cisco_inventory(output):
    """
    Parse Cisco 'show inventory' output to extract model and SFP count.
    """
    # Placeholder: Implement your Cisco output parsing logic here
    model = None
    sfp_count = 0
    for line in output.splitlines():
        if "PID:" in line:
            try:
                model = line.split("PID:")[1].split(",")[0].strip()
            except Exception:
                continue
        if "SFP" in line:
            sfp_count += 1
    return model, sfp_count

def inventory_task(device, device_type):
    """
    Task to collect inventory information from a device.
    Only returns a result dict if successful. Errors go to error.log.
    """
    ip = device.get("host")
    if not validate_ip(ip):
        msg = f"Invalid IP address: {ip}"
        error_logger.error(f"{device.get('name', 'UNKNOWN')} ({ip}): {msg}")
        return None
    try:
        inventory = get_device_inventory(device, device_type)
        # Parse inventory output for model and SFP count
        if device_type == "arista_eos":
            model, sfp_count = parse_arista_inventory(inventory)
        elif device_type == "cisco_ios":
            model, sfp_count = parse_cisco_inventory(inventory)
        else:
            model, sfp_count = None, 0
        result = {
            "device": device.get("name", "UNKNOWN"),
            "host": ip,
            "model": model,
            "sfp_count": sfp_count,
            "status": "SUCCESS",
        }
        logger.info(f"Inventory SUCCESS: {device.get('name', 'UNKNOWN')} ({ip})")
        return result
    except Exception as e:
        error_logger.error(f"Inventory FAILED: {device.get('name', 'UNKNOWN')} ({ip}): {str(e)}")
        return None

def main():
    config = load_yaml(CONFIG_FILE_PATH)
    thread_params = config.get("thread_pools", {})
    num_threads = thread_params.get("num_threads", 5)

    devices_yaml = load_yaml(DEVICES_FILE_PATH)
    devices = devices_yaml.get("devices", [])
    if not devices:
        logger.critical("No devices found for inventory collection.")
        return

    results = []
    any_failed = False
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for device in devices:
            group = device.get("group")
            device_type = GROUP_TO_DEVICE_TYPE.get(group)
            if not device_type:
                logger.error(f"Unknown group '{group}' for device {device['name']}")
                any_failed = True
                continue

            futures.append(executor.submit(inventory_task, device, device_type))


        for future in as_completed(futures):
            result = future.result()
            if result is None:
                any_failed = True
                continue
            if result["status"] != "SUCCESS":
                any_failed = True
            if result["status"] == "SUCCESS":
                results.append(result)


    output_dir = os.path.dirname(INVENTORY_RESULT_FILE_PATH)
    os.makedirs(output_dir, exist_ok=True)
    with open(INVENTORY_RESULT_FILE_PATH, "w") as f:
        yaml.dump(results, f, default_flow_style=False, allow_unicode=True)
    logger.info(f"Inventory results written to {INVENTORY_RESULT_FILE_PATH}")
    return results, any_failed

if __name__ == "__main__":
    main()
