# utils/credentials_utils.py

import yaml

def load_credentials(credentials_file, device_name):
    with open(credentials_file, "r") as f:
        creds = yaml.safe_load(f)
    
    # First check if the device has specific overrides
    if "overrides" in creds and device_name in creds["overrides"]:
        c = creds["overrides"][device_name]
        return c.get("username"), c.get("password"), c.get("enable_secret")
    # Otherwise, check for a default set of credentials
    elif "default" in creds:
        c = creds["default"]
        return c.get("username"), c.get("password"), c.get("enable_secret")
    else:
        raise ValueError(f"No credentials found for device {device_name}")

