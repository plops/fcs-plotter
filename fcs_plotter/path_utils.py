from pathlib import Path


def get_project_root() -> Path:
    """Returns the project root directory."""
    return Path(__file__).parent.parent


def get_config_file() -> Path:
    """Returns the path to the configuration file."""
    return get_project_root() / "config" / "config.yaml"


def get_log_dir() -> Path:
    """Returns the path to the log directory."""
    log_dir = get_project_root() / "logs"
    log_dir.mkdir(exist_ok=True)
    return log_dir


def get_cache_dir() -> Path:
    """Returns the path to the cache directory."""
    cache_dir = get_project_root() / "cache"
    cache_dir.mkdir(exist_ok=True)
    return cache_dir
