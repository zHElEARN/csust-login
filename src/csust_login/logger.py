import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

from .config import config


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.hasHandlers():
        return logger

    logger.propagate = False

    if config.ENABLE_LOGGING:
        level_str = getattr(config, "LOG_LEVEL", "INFO").upper()
        log_level = getattr(logging, level_str, logging.INFO)
        logger.setLevel(log_level)

        os.makedirs(config.LOG_DIR, exist_ok=True)
        formatter = logging.Formatter(f"%(asctime)s - {name} - %(levelname)s - %(message)s")

        log_filepath = os.path.join(config.LOG_DIR, "app.log")

        file_handler = TimedRotatingFileHandler(
            filename=log_filepath,
            when="midnight",
            interval=1,
            backupCount=7,
            encoding="utf-8",
            utc=False,
        )
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    else:
        logger.addHandler(logging.NullHandler())

    return logger
