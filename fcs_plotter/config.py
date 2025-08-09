import yaml
from pathlib import Path
from .path_utils import get_config_file


def load_config(config_path: Path = None) -> dict:
    """Loads the YAML configuration file."""
    if config_path is None:
        config_path = get_config_file()

    if not config_path.exists():
        # Return default config if file doesn't exist
        return {
            "logging": {
                "log_file": "logs/app.log",
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "date_format": "%Y-%m-%dT%H:%M:%S%z"
            },
            "cache": {
                "directory": "cache"
            },
            "plotting": {
                "default_x_channel": "FSC-A",
                "default_y_channel": "SSC-A"
            }
        }

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config


config = load_config()
