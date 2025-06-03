import questionary
import sys
from scripts import config_manager, backup_manager, inventory_manager, firmware_manager

def main_menu():
    while True:
        action = questionary.select(
            "Choose a task to perform:",
            choices=[
                "Configuration Deployment",
                "Backup Devices",
                "Inventory Collection",
                "Firmware Upgrade",
                "Exit"
            ]
        ).ask()

        if action == "Configuration Deployment":
            print("Running configuration deployment...")
            config_manager.main()
        elif action == "Backup Devices":
            print("Running backup...")
            backup_manager.main()
        elif action == "Inventory Collection":
            print("Running inventory collection...")
            inventory_manager.main()
        elif action == "Firmware Upgrade":
            print("Firmware upgrade not implemented yet.")
            # firmware_manager.main()
        elif action == "Exit":
            print("Exiting...")
            sys.exit(0)
        else:
            print("Unknown action!")

if __name__ == "__main__":
    main_menu()
