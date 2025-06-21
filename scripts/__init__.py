# scripts/__init__.py
# -*- coding: utf-8 -*-
# This file is part of the Network Automation Suite.

VERSION = "1.9.2"

def print_banner():
    print(f"Network Automation Suite v{VERSION}")


from .config_manager import *
from .backup_manager import *
from .inventory_manager import *
from .firmware_manager import *


# Sample imports for the modules that might be used in the scripts package.
# from scripts import config_manager
# from scripts import backup_manager
# from scripts import inventory_manager
# from scripts import firmware_manager