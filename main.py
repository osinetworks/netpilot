import argparse
from scripts import config_manager, backup_manager, inventory_manager, firmware_manager
from utils.logger_utils import logger_handler

logger = logger_handler("netpilot")

def main():
    """
    Main entry point for the network automation script.
    """
    logger.info("Starting Network Automation Suite - NetPilot")
    parser = argparse.ArgumentParser(
        description="Network Automation Main Entry Point"
    )
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

    task_map = {
        "config": config_manager,
        "backup": backup_manager,
        "inventory": inventory_manager,
        "firmware": firmware_manager,
    }

    task_module = task_map.get(args.task)
    if not task_module:
        logger.error(f"Unsupported task: {args.task}")
        return

    logger.info(f"Starting {args.task} task.")
    try:
        task_module.main()
        logger.info(f"{args.task.capitalize()} task finished.")
    except Exception as exc:
        logger.exception(f"{args.task.capitalize()} task failed: {exc}")

if __name__ == "__main__":
    main()
