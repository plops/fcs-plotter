import pandas as pd
import readfcs
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
        adata = readfcs.read(str(file_path))
        df = adata.to_df()
        # Extract metadata if available
        metadata = getattr(adata, 'uns', {}) if hasattr(adata, 'uns') else {}
        logger.info(f"Successfully read {file_path}")
        return df, metadata
    except Exception as e:
        logger.error(f"Failed to read FCS file {file_path}: {e}")
        return None, None
