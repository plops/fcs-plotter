import logging
import sys
from logging.handlers import RotatingFileHandler
from .config import config
from .path_utils import get_project_root


class UTCFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        import datetime

        dt = datetime.datetime.fromtimestamp(record.created, tz=datetime.timezone.utc)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.isoformat()


def setup_logger():
    """Sets up the application logger."""
    log_config = config["logging"]
    log_file_path = get_project_root() / log_config["log_file"]
    log_file_path.parent.mkdir(exist_ok=True)

    logger = logging.getLogger("fcs_plotter")
    logger.setLevel(log_config["level"])

    formatter = UTCFormatter(
        fmt=log_config["format"], datefmt=log_config["date_format"]
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    file_handler = RotatingFileHandler(
        log_file_path, maxBytes=10 * 1024 * 1024, backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger()
