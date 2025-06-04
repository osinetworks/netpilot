import csv
import yaml

FILEPATH = "devices.csv"

# Vendor group settings:
group_map = {
    "cisco": "cisco",
    "arista": "arista"
}

# A Counter which gives automatic names for devices:
vendor_count = {
    "cisco": 1,
    "arista": 1
}

devices = []

# Read CSV file:
with open(FILEPATH) as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        if row == [] or len(row) < 2:
            continue
        
        host = row[0].strip()
        vendor = row[1].strip().lower()
        group = group_map.get(vendor, "unknown")

        # Create device name:
        devname = f"{vendor}-sw-{vendor_count[vendor]:03}"
        vendor_count[vendor] += 1

        devices.append({
            "name": devname,
            "host": host,
            "group": group
        })

# Top level structure for devices.yaml:
devices_yaml = {
    "defaults": {
        "username": "admin",
        "password": "admin"
    },
    "groups": {
        "unknown": {
            "device_type": "unknown"
        },
        "cisco": {
            "device_type": "cisco_ios",
            "enable_secret": "admin"
        },
        "arista": {
            "device_type": "arista_eos"
        }
    },
    "devices": devices
}

# YAML output:
with open("devices.yaml", "w") as yamlfile:
    yaml.dump(devices_yaml, yamlfile, default_flow_style=False, sort_keys=False, allow_unicode=True)

print("devices.yaml successfully created.")

