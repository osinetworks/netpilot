# scripts/config_parser.py

import yaml
import logging
from utils.exceptions import ConfigFileError

logger = logging.getLogger("config_parser")

def load_yaml(path):
    """
    Load and validate a YAML file.
    Raises ConfigFileError on parse or file errors.
    """
    try:
        with open(path, "r") as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        logger.error(f"YAML syntax error in {path}: {e}")
        raise ConfigFileError(f"YAML syntax error in {path}: {e}")
    except Exception as e:
        logger.error(f"Could not open YAML file {path}: {e}")
        raise ConfigFileError(f"Could not open YAML file {path}: {e}")

