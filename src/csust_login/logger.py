import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

from .config import config

_initialized = False


def get_logger(name: str) -> logging.Logger:
    global _initialized
    logger = logging.getLogger(name)

    logger.propagate = True

    if not _initialized:
        root = logging.getLogger()
        level_str = getattr(config, "LOG_LEVEL", "INFO").upper()
        log_level = getattr(logging, level_str, logging.INFO)
        root.setLevel(log_level)

        if config.ENABLE_LOGGING:
            os.makedirs(config.LOG_DIR, exist_ok=True)
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", "%H:%M:%S")

            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            root.addHandler(console_handler)

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
            root.addHandler(file_handler)
        else:
            root.addHandler(logging.NullHandler())

        _initialized = True

    return logger
