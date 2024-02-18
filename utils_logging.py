# utils_logging.py
import logging.config
import yaml
import os
import os
import shutil
from pathlib import Path

from utils import project_absolute_path

def setup_logging(
        log_config_path='logging.yaml',
        default_level=logging.INFO,
):
    """Setup logging configuration"""

    # Set up logs folder
    logs_folder = str(project_absolute_path()) + '/logs'
    if os.path.exists(logs_folder):
        shutil.rmtree(logs_folder)
    Path(logs_folder).mkdir(parents=True, exist_ok=True)

    # Config logger
    if os.path.exists(log_config_path):
        with open(log_config_path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

def close_log_handlers():
    for handler in logging.root.handlers[:]:
        handler.close()
        logging.root.removeHandler(handler)