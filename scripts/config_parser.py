# scripts/config_parser.py

import yaml
import streamlit as st
from utils.exceptions import ConfigFileError
from utils.logger_utils import setup_logger

logger = setup_logger("config_parser")

def load_yaml(file_path):
    """
    Load and validate a YAML file.
    Raises ConfigFileError on parse or file errors.
    """
    try:
        with open(file_path, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.error(f"YAML file not found: {file_path}")
        st.error(f"YAML file not found: {file_path}")
        raise ConfigFileError(f"YAML file not found: {file_path}")
    except yaml.YAMLError as e:
        logger.error(f"YAML syntax error in {file_path}: {e}")
        st.error(f"YAML syntax error in {file_path}: {e}")
        raise ConfigFileError(f"YAML syntax error in {file_path}: {e}")
    except Exception as e:
        logger.error(f"Could not open YAML file {file_path}: {e}")
        st.error(f"Could not open YAML file {file_path}: {e}")
        raise ConfigFileError(f"Could not open YAML file {file_path}: {e}")

