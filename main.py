import argparse
import logging
from scripts import config_manager
from scripts import backup_manager
from scripts import inventory_manager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s]: %(message)s",
)


def main():
    """
    Main entry point for the network automation script.
    This script handles different automation tasks such as configuration deployment,
    backup, inventory management, and firmware updates.
    """
    logging.info("Starting Network Automation Suite - NetPilot")
    parser = argparse.ArgumentParser(description="Network Automation Main Entry Point")
    parser.add_argument(
        "--task",
        required=True,
        choices=["config", "backup", "inventory", "firmware"],
        metavar="TASK",
        type=str,
        default="config",
        nargs="?",
        dest="task",
        help="Automation task to run (example: config)"
    )

    args = parser.parse_args()

    if args.task == "config":
        logging.info("Starting config deployment task.")
        config_manager.main()
        logging.info("Config deployment task finished.")
    elif args.task == "backup":
        logging.info("Starting backup task.")
        backup_manager.main()
        logging.info("Backup task finished.")
    elif args.task == "inventory":
        logging.info("Starting inventory task.")
        inventory_manager.main()
        logging.info("Inventory task finished.")
    else:
        logging.error(f"Unsupported task: {args.task}")

if __name__ == "__main__":
    main()
