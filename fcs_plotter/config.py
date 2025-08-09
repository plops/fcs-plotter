import yaml
from pathlib import Path
from .path_utils import get_config_file


def load_config(config_path: Path = get_config_file()) -> dict:
    """Loads the YAML configuration file."""
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config


config = load_config()
