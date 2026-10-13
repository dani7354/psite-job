import logging
from datetime import datetime
from pathlib import Path

from psitejob.configuration.configuration import Configuration

LOG_FILE_DATE_FORMAT = "%Y-%m-%d"


def setup_logging(configuration: Configuration, filename_base: str) -> None:
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    file_path = Path(configuration.log_dir) / f"{filename_base}_{datetime.now().strftime(LOG_FILE_DATE_FORMAT)}.log"
    file_handler = logging.FileHandler(file_path)
    file_handler.setFormatter(formatter)

    log_level = logging.DEBUG if configuration.test_mode_enabled else logging.INFO
    logger = logging.getLogger()
    logger.setLevel(log_level)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
