import os
import hashlib
from datetime import datetime
from datetime import time as t
from netmiko import ConnectHandler, file_transfer
from time import sleep
from scripts.constants import (
    BACKUP_FOLDER_PATH,
    INVENTORY_COMMANDS_PATHS,
    BACKUP_COMMANDS_PATHS,
    CREDENTIALS_FILE_PATH,
    FIRMWARE_CONFIG_PATH
)
from scripts.config_parser import load_yaml
from utils.credentials_utils import load_credentials


def load_commands_from_file(file_path):
    """Loads commands from a file, ignoring empty lines and comments."""

    commands = []
    with open(file_path, "r") as f:
        for line in f:
            cmd = line.strip()
            if cmd and not cmd.startswith("!"):
                commands.append(cmd)
    return commands


def _get_md5sum(file_path):
    """Return md5 hash of a local file."""

    h = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()


def _parse_free_space(output):
    """Parse 'dir flash:' output to get free MB."""

    for line in output.splitlines():
        if "bytes free" in line:
            try:
                free_bytes = int(line.strip().split()[0])
                return free_bytes // (1024 * 1024)
            except Exception:
                continue
    return 0


def _parse_old_firmwares(output, desired_firmware):
    """Return .bin files except for the desired one."""

    bins = []
    for line in output.splitlines():
        if line.endswith(".bin") and desired_firmware not in line:
            bins.append(line.split()[-1])
    return bins


def _get_switch_time(net_connect):
    """Returns (hour, minute) from switch clock."""

    output = net_connect.send_command("show clock")
    try:
        parts = output.strip().split()
        dt_str = " ".join(parts[-5:])
        dt_obj = datetime.strptime(dt_str, "%b %d %H:%M:%S %Y")
        return dt_obj.hour, dt_obj.minute
    except Exception:
        return None, None


def _set_switch_time(net_connect, ref_dt=None):
    """Sets switch time to system time or provided datetime."""

    if ref_dt is None:
        ref_dt = datetime.now()
    cmd = f"clock set {ref_dt.strftime('%H:%M:%S')} {ref_dt.strftime('%d %b %Y')}"
    net_connect.send_config_set([cmd])


def _get_reload_time(hour, minute, reload_times):
    """Returns next reload time (str) according to policy."""

    before = reload_times["before"]
    after = reload_times["after"]
    h1, m1 = map(int, before.split(":"))
    h2, m2 = map(int, after.split(":"))
    
    current = t(hour, minute)
    before_time = t(h1, m1)
    after_time = t(h2, m2)
    if current < before_time:
        return before
    else:
        return after


def get_device_inventory(device, device_type):
    """Retrieves the inventory information from a network device using Netmiko."""

    commands_file = INVENTORY_COMMANDS_PATHS.get(device_type)
    if not commands_file:
        raise ValueError(f"No inventory commands file for device type {device_type}")
    commands = load_commands_from_file(commands_file)

    username, password, enable_secret = load_credentials(CREDENTIALS_FILE_PATH, device.get("name", device["host"]))
    connection_params = {
        "device_type": device_type,
        "host": device["host"],
        "username": username,
        "password": password,
        "secret": enable_secret if enable_secret else password,
    }

    all_output = ""
    with ConnectHandler(**connection_params) as net_connect:
        net_connect.enable()
        for cmd in commands:
            output = net_connect.send_command(cmd, expect_string=r"#")
            all_output += f"\n\n> {cmd}\n{output}"
    print(f"All inputs:\n{all_output.strip()}")
    return all_output.strip()


def push_config_to_device(device, commands, device_type):
    """Push configuration commands to a network device using Netmiko."""
    
    username, password, enable_secret = load_credentials(CREDENTIALS_FILE_PATH, device.get("name", device["host"]))
    connection_params = {
        "device_type": device_type,
        "host": device["host"],
        "username": username,
        "password": password,
        "secret": enable_secret if enable_secret else password,
    }
    output = ""
    with ConnectHandler(**connection_params) as net_connect:
        net_connect.enable()
        output += net_connect.send_config_set(commands)
        output += "\n" + net_connect.save_config()
    return output


def backup_device_config(device, device_type):
    """
    Backs up device config using Netmiko and commands from BACKUP_COMMANDS_PATHS.
    """
    commands_file = BACKUP_COMMANDS_PATHS.get(device_type)
    if not commands_file:
        raise ValueError(f"No backup commands file for device type {device_type}")
    commands = load_commands_from_file(commands_file)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = device.get("name", device["host"])
    output_dir = BACKUP_FOLDER_PATH
    os.makedirs(output_dir, exist_ok=True)
    files = []
    output = ""

    username, password, enable_secret = load_credentials(CREDENTIALS_FILE_PATH, device.get("name", device["host"]))
    connection_params = {
        "device_type": device_type,
        "host": device["host"],
        "username": username,
        "password": password,
        "secret": enable_secret if enable_secret else password,
    }

    with ConnectHandler(**connection_params) as net_connect:
        net_connect.enable()
        for cmd in commands:
            cmd_output = net_connect.send_command(cmd, expect_string=r"#")
            fname_part = cmd.replace(" ", "_").replace("/", "_")
            filename = f"{base_name}_{fname_part}_{timestamp}.txt"
            file_path = os.path.join(output_dir, filename)
            with open(file_path, "w") as f:
                f.write(cmd_output)
            files.append(file_path)
            output += f"\n> {cmd}\n{cmd_output}"
    return files, output.strip()


def detect_device_vendor(device):
    """
    Detect device vendor by running 'show version' or equivalent.
    Returns string: 'arista', 'cisco', etc.
    """
    try:
        username, password, enable_secret = load_credentials(CREDENTIALS_FILE_PATH, device.get("name", device["host"]))
        for device_type in ["arista_eos", "cisco_ios", "juniper_junos"]:
            connection_params = {
                "device_type": device_type,
                "host": device["host"],
                "username": username,
                "password": password,
                "secret": enable_secret if enable_secret else password,
            }
            try:
                with ConnectHandler(**connection_params) as net_connect:
                    out = net_connect.send_command("show version", expect_string=r"#|>")
                    out_lower = out.lower()
                    if "arista" in out_lower:
                        return "arista"
                    elif "cisco" in out_lower:
                        return "cisco"
                    elif "juniper" in out_lower:
                        return "juniper"
            except Exception:
                continue
        return "unknown"
    except Exception as e:
        return "unknown"


def firmware_upgrade_procedure(device, device_type, logger):
    """
    Dispatches firmware upgrade to the correct vendor procedure.
    Loads firmware config, normalizes type, logs errors if unsupported.
    """
    from scripts.config_parser import load_yaml
    from scripts.constants import FIRMWARE_CONFIG_PATH

    # Load firmware config (firmware.yaml)
    firmware_config = load_yaml(FIRMWARE_CONFIG_PATH)
    if firmware_config is None:
        logger.error("Firmware config file could not be loaded or is empty.")
        return "Firmware config file could not be loaded or is empty."

    fw_info = firmware_config.get(device_type)
    if not fw_info:
        logger.error(f"Firmware config for device_type '{device_type}' is missing in firmware.yaml.")
        return f"Firmware config for device_type '{device_type}' is missing in firmware.yaml."

    # Dispatch according to device_type
    device_type = device_type.lower()
    if device_type == "arista_eos":
        return arista_firmware_procedure(device, fw_info, logger)
    elif device_type == "cisco_ios":
        return cisco_firmware_procedure(device, fw_info, logger)
    else:
        logger.error(f"Firmware upgrade not supported for device_type {device_type}.")
        return f"Firmware upgrade not supported for device_type {device_type}."


def arista_firmware_procedure(device, config, logger):
    """
    All steps for Arista firmware upgrade.
    - Checks MD5 hash
    - Checks flash usage
    - Removes unused .bin if needed
    - Copies firmware if needed
    - Verifies firmware MD5
    - Sets boot system
    - Sets/syncs clock
    - Schedules reload at specified time
    """

    fw_path = config["firmware"]["file_path"]
    fw_name = config["firmware"]["file_name"]
    md5_path = config["firmware"]["md5sum_path"]
    min_free_mb = config["firmware"].get("min_free_mb", 800)
    reload_times = config.get("reload_times", {"before": "12:30", "after": "20:30"})

    # Step 1: MD5 hash check local
    if not os.path.exists(fw_path) or not os.path.exists(md5_path):
        logger.error(f"Firmware or hash file missing: {fw_path} / {md5_path}")
        print("Firmware or hash file missing. Check config and try again.")
        return
    with open(md5_path) as f:
        expected_md5 = f.read().strip()
    actual_md5 = _get_md5sum(fw_path)
    if expected_md5 != actual_md5:
        logger.error(f"Local firmware MD5 mismatch! Expected: {expected_md5} Got: {actual_md5}")
        print("Local firmware MD5 mismatch! Check your firmware file or hash.")
        return

    username, password, enable_secret = load_credentials(CREDENTIALS_FILE_PATH, device.get("name", device["host"]))
    connection_params = {
        "device_type": "arista_eos",
        "host": device["host"],
        "username": username,
        "password": password,
        "secret": enable_secret if enable_secret else password,
    }

    try:
        with ConnectHandler(**connection_params) as net_connect:
            logger.info(f"Connected to {device['name']} ({device['host']})")

            # Step 2: Flash usage & cleanup
            flash_dir = net_connect.send_command("dir flash:")
            free_mb = _parse_free_space(flash_dir)
            logger.info(f"Free flash: {free_mb} MB")
            if free_mb < min_free_mb:
                old_bins = _parse_old_firmwares(flash_dir, fw_name)
                for binfile in old_bins:
                    net_connect.send_command(f"delete flash:{binfile}")
                    logger.info(f"Deleted old firmware: {binfile}")
                sleep(3)
                flash_dir = net_connect.send_command("dir flash:")
                free_mb = _parse_free_space(flash_dir)
                if free_mb < min_free_mb:
                    logger.error(f"Not enough free flash on {device['name']}")
                    print("Insufficient flash space after cleanup!")
                    return

            # Step 3: Copy firmware if not present
            if fw_name not in flash_dir:
                logger.info(f"Transferring firmware {fw_name} to device...")
                transfer_result = file_transfer(
                    net_connect,
                    source_file=fw_path,
                    dest_file=fw_name,
                    file_system="flash:",
                    direction="put",
                    overwrite_file=True,
                    disable_md5=True,
                )
                if not transfer_result["file_exists"]:
                    logger.error("Firmware file transfer failed.")
                    print("File transfer failed!")
                    return
                logger.info(f"Firmware {fw_name} copied to switch.")

            # Step 4: MD5 verify on device
            output = net_connect.send_command(f"verify /md5 flash:{fw_name}")
            if expected_md5 not in output:
                logger.error(f"MD5 mismatch for {fw_name} on {device['name']}")
                print("MD5 mismatch after copy!")
                return
            logger.info("MD5 hash verified on device.")

            # Step 5: Set boot system, save config
            net_connect.send_config_set([f"boot system flash:{fw_name}"])
            net_connect.save_config()
            logger.info("Boot system set and config saved.")

            # Step 6: Clock check/set
            hour, minute = _get_switch_time(net_connect)
            if hour is None:
                _set_switch_time(net_connect)
                hour, minute = _get_switch_time(net_connect)
            reload_at = _get_reload_time(hour, minute, reload_times)
            logger.info(f"Scheduled reload at {reload_at}")

            # Step 7: Schedule reload
            net_connect.send_command(f"reload at {reload_at}")
            logger.info(f"Reload scheduled at {reload_at} on {device['name']}")

            print(f"Firmware successfully upgraded and reload scheduled for {device['name']}")
            logger.info(f"Firmware successfully upgraded on {device['name']}")
    except Exception as e:
        logger.error(f"Firmware upgrade failed for {device.get('name','unknown')}: {e}")
        print(f"Error upgrading firmware on {device.get('name','unknown')}: {e}")


def cisco_firmware_procedure(device, config, logger):
    """
    Placeholder for Cisco firmware upgrade procedure.
    Currently not implemented.
    """
    logger.warning("Cisco firmware upgrade procedure is not yet implemented.")
    # Implement Cisco-specific firmware upgrade logic here
    pass
