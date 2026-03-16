import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

from .config import config

_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def _get_log_level() -> int:
    level_str = getattr(config, "LOG_LEVEL", "INFO").upper()
    return getattr(logging, level_str, logging.INFO)


def setup_cli_logging() -> None:
    root = logging.getLogger()
    log_level = _get_log_level()
    root.setLevel(log_level)

    formatter = logging.Formatter(_LOG_FORMAT)

    # 控制台 handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    root.addHandler(console_handler)

    # 文件 handler
    if config.ENABLE_LOGGING:
        os.makedirs(config.LOG_DIR, exist_ok=True)
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
        file_handler.setLevel(log_level)
        root.addHandler(file_handler)


def setup_ui_logging(qt_handler: logging.Handler) -> None:
    root = logging.getLogger()
    log_level = _get_log_level()
    root.setLevel(log_level)
    qt_handler.setLevel(log_level)
    root.addHandler(qt_handler)
