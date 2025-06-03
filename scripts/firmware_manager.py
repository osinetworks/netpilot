import os
import yaml
import logging
from scripts.constants import DEVICES_FILE_PATH, FIRMWARE_CONFIG_PATH
from scripts.netmiko_utils import detect_device_vendor, arista_firmware_procedure, cisco_firmware_procedure
from scripts.config_parser import load_yaml

logger = logging.getLogger("firmware_manager")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s'))
logger.addHandler(console_handler)

def main():
    # Load device list and firmware config
    devices_yaml = load_yaml(DEVICES_FILE_PATH)
    devices = devices_yaml.get("devices", [])
    config = load_yaml(FIRMWARE_CONFIG_PATH)

    for device in devices:
        logger.info(f"Connecting to {device.get('name','unknown')} ({device.get('host','')}) for vendor detection...")
        vendor = detect_device_vendor(device)
        logger.info(f"Detected vendor: {vendor}")

        if vendor == "arista":
            logger.info("Starting Arista firmware procedure...")
            try:
                arista_firmware_procedure(device, config, logger)
            except Exception as e:
                logger.error(f"Arista firmware upgrade failed for {device.get('name','unknown')}: {e}")
        elif vendor == "cisco":
            logger.info("Starting Cisco firmware procedure...")
            try:
                cisco_firmware_procedure(device, config, logger)
            except Exception as e:
                logger.error(f"Cisco firmware upgrade failed for {device.get('name','unknown')}: {e}")
        else:
            logger.warning(f"Unsupported or unknown device vendor: {vendor}")

    logger.info("Firmware upgrade process finished for all devices.")

if __name__ == "__main__":
    main()
