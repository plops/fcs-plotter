import pandas as pd
from readfcs import read
from joblib import Memory
from .path_utils import get_cache_dir
from .logger_setup import logger

# Setup caching
cache_dir = get_cache_dir()
memory = Memory(cache_dir, verbose=0)


@memory.cache
def load_fcs_file(file_path: str) -> tuple[pd.DataFrame, dict]:
    """
    Reads an FCS file and returns the data and metadata.
    Results are cached to disk.
    """
    try:
        logger.info(f"Reading FCS file: {file_path}")
        data, metadata = read(file_path)
        logger.info(f"Successfully read {file_path}")
        return data, metadata
    except Exception as e:
        logger.error(f"Failed to read FCS file {file_path}: {e}")
        return None, None
