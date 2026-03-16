import os
from dataclasses import dataclass
from typing import Dict, TypeVar, cast

import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

T = TypeVar("T")


def get_env_or_fatal(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise ValueError(f"必须设置环境变量 {key}")
    return value


def get_env_or_default(key: str, default: T) -> T:
    value = os.getenv(key)
    if value is None:
        return default
    if isinstance(default, bool):
        return cast(T, value.lower() == "true")
    return type(default)(value)


@dataclass
class AppConfig:
    USERNAME: str
    PASSWORD: str

    DAEMON_EXEC_INTERVAL: int
    DAEMON_RETRY_INTERVAL: int

    CHECK_NETWORK_TIMEOUT: int
    LOGIN_TIMEOUT: int

    NETWORK_RESET_CMD: str
    NETWORK_RESET_TIMEOUT: int
    NETWORK_RESET_WAIT: int

    ENABLE_LOGGING: bool
    LOG_DIR: str
    LOG_LEVEL: str

    PROXIES: Dict[str, str]

    @classmethod
    def load(cls) -> "AppConfig":
        return cls(
            USERNAME=get_env_or_fatal("CSUST_USERNAME"),
            PASSWORD=get_env_or_fatal("CSUST_PASSWORD"),
            DAEMON_EXEC_INTERVAL=get_env_or_default("DAEMON_EXEC_INTERVAL", 20),
            DAEMON_RETRY_INTERVAL=get_env_or_default("DAEMON_RETRY_INTERVAL", 3),
            CHECK_NETWORK_TIMEOUT=get_env_or_default("CHECK_NETWORK_TIMEOUT", 5),
            LOGIN_TIMEOUT=get_env_or_default("LOGIN_TIMEOUT", 10),
            NETWORK_RESET_CMD=get_env_or_default("NETWORK_RESET_CMD", ""),
            NETWORK_RESET_TIMEOUT=get_env_or_default("NETWORK_RESET_TIMEOUT", 20),
            NETWORK_RESET_WAIT=get_env_or_default("NETWORK_RESET_WAIT", 5),
            ENABLE_LOGGING=get_env_or_default("ENABLE_LOGGING", True),
            LOG_DIR=get_env_or_default("LOG_DIR", "logs"),
            LOG_LEVEL=get_env_or_default("LOG_LEVEL", "INFO"),
            PROXIES={"http": "", "https": ""},
        )


config = AppConfig.load()
