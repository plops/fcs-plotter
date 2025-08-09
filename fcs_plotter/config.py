import yaml
from .path_utils import get_config_file

# Load configuration
with open(get_config_file(), 'r') as f:
    config = yaml.safe_load(f)
