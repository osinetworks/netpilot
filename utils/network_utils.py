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
