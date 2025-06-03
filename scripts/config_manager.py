import yaml
import logging
import ipaddress
import socket
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from scripts.constants import (
    CONFIG_FILE_PATH,
    DEVICES_FILE_PATH,
    OUTPUT_FOLDER,
    COMMANDS_PATHS,
    GROUP_TO_DEVICE_TYPE,
    INFO_LOG_PATH,
    DEBUG_LOG_PATH,
    ERROR_LOG_PATH,
    CONFIG_RESULT_FILE_PATH
)
from scripts.netmiko_utils import push_config_to_device
from scripts.worker import device_worker
from scripts.config_parser import load_yaml
from utils.network_utils import validate_ip, is_reachable

os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("config_manager")
logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all logs

# Console Handler (optional)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s'))
logger.addHandler(console_handler)

# Info log handler
info_handler = logging.FileHandler(INFO_LOG_PATH)
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s'))
info_handler.addFilter(lambda record: record.levelno == logging.INFO)
logger.addHandler(info_handler)

# Debug log handler
debug_handler = logging.FileHandler(DEBUG_LOG_PATH)
debug_handler.setLevel(logging.DEBUG)
debug_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s'))
logger.addHandler(debug_handler)

# Error log handler
error_handler = logging.FileHandler(ERROR_LOG_PATH)
error_handler.setLevel(logging.WARNING)
error_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s'))
logger.addHandler(error_handler)


def get_config_commands(device_type):
    """Return config commands file path according to device type."""
    try:
        return COMMANDS_PATHS[device_type]
    except KeyError:
        raise ValueError(f"Unsupported device_type: {device_type}")


def load_commands(file_path):
    """Load config commands from a file."""
    with open(file_path, "r") as f:
        commands = [line.strip() for line in f if line.strip() and not line.startswith("!")]
    return commands


def run_config_task(device, commands, device_type):
    """
    Thread worker for pushing config to a single device,
    with IP and reachability check. Logs output in detail.
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
        logger.error(f"Invalid IP address for device {result['device']}: {ip}")
        return result

    if not is_reachable(ip):
        result["output"] = f"IP not reachable on port 22: {ip}"
        logger.error(f"Device unreachable (port 22) for {result['device']}: {ip}")
        return result

    try:
        output = push_config_to_device(device, commands, device_type)
        result["status"] = "SUCCESS"
        result["output"] = output
        logger.info(f"Config push SUCCESS: {result['device']} ({ip})")
        logger.info(f"Device output:\n{output}")
    except Exception as e:
        result["output"] = str(e)
        logger.error(f"Config push FAILED: {result['device']} ({ip}): {e}")
    return result


def validate_devices(devices):
    """
    Validate devices.yaml for required keys and 
    check for comma instead of dot errors in IP.
    Returns a list of valid devices.
    """

    valid_devices = []
    for dev in devices:
        if "name" not in dev or "host" not in dev or "group" not in dev:
            logger.error(f"Missing fields in device entry: {dev}")
            continue

        ip = dev["host"]
        if "," in ip:
            logger.error(f"Possible comma instead of dot in IP address: {ip} (device {dev['name']})")
            continue

        if not validate_ip(ip):
            logger.error(f"Invalid IP address format: {ip} (device {dev['name']})")
            continue

        valid_devices.append(dev)
    return valid_devices


def main():
    """Main function to load config, devices, and run tasks in parallel."""
    
    config = load_yaml(CONFIG_FILE_PATH)
    thread_params = config.get("thread_pools", {})
    num_threads = thread_params.get("num_threads", 5)
    
    devices_yaml = load_yaml(DEVICES_FILE_PATH)
    devices = devices_yaml.get("devices", [])

    devices = validate_devices(devices)
    if not devices:
        logger.critical("No valid devices found. Exiting.")
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
            try:
                commands_file = get_config_commands(device_type)
                commands = load_commands(commands_file)
            except Exception as e:
                logger.error(f"Command file loading failed for {device['name']}: {e}")
                continue
            #futures.append(executor.submit(run_config_task, device, commands, device_type)
            executor.submit(device_worker, run_config_task, device, commands, device_type)

        for future in as_completed(futures):
            results.append(future.result())

    output_file = os.path.join(CONFIG_RESULT_FILE_PATH)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        yaml.dump(results, f, default_flow_style=False, allow_unicode=True)
    logger.info(f"Config deployment results written to {output_file}")


if __name__ == "__main__":
    main()
