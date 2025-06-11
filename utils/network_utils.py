# utils/network_utils.py

import ipaddress
import socket

def validate_ip(ip_str):
    """Check if the IP address is valid."""
    try:
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False

def is_reachable(ip, timeout=2):
    """Check if the device is reachable on TCP 22 (SSH)."""
    try:
        sock = socket.create_connection((ip, 22), timeout=timeout)
        sock.close()
        return True
    except Exception:
        return False


def validate_devices(devices, logger):
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