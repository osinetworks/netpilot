# scripts/worker.py

import logging

def device_worker(task_func, device, *args, **kwargs):
    """
    Generic worker for any device task (config, backup, etc.).
    Handles logging, exception and result.
    """
    logger = logging.getLogger("worker")
    try:
        logger.info(f"Starting task for {device.get('name')}")
        result = task_func(device, *args, **kwargs)
        logger.info(f"Task SUCCESS for {device.get('name')}")
        return result
    except Exception as e:
        logger.error(f"Task FAILED for {device.get('name')}: {e}")
        return {"device": device.get("name"), "status": "FAILED", "output": str(e)}

