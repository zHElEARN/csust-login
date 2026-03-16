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

    ENABLE_LOGGING: bool
    LOG_DIR: str
    LOG_LEVEL: str

    CHECK_NETWORK_TIMEOUT: int
    LOGIN_TIMEOUT: int
    GET_LOCATION_TIMEOUT: int

    PROXIES: Dict[str, str]

    @classmethod
    def load(cls) -> "AppConfig":
        return cls(
            USERNAME=get_env_or_fatal("CSUST_USERNAME"),
            PASSWORD=get_env_or_fatal("CSUST_PASSWORD"),
            DAEMON_EXEC_INTERVAL=get_env_or_default("DAEMON_EXEC_INTERVAL", 20),
            DAEMON_RETRY_INTERVAL=get_env_or_default("DAEMON_RETRY_INTERVAL", 3),
            ENABLE_LOGGING=get_env_or_default("ENABLE_LOGGING", True),
            LOG_DIR=get_env_or_default("LOG_DIR", "logs"),
            LOG_LEVEL=get_env_or_default("LOG_LEVEL", "INFO"),
            CHECK_NETWORK_TIMEOUT=get_env_or_default("CHECK_NETWORK_TIMEOUT", 5),
            LOGIN_TIMEOUT=get_env_or_default("LOGIN_TIMEOUT", 10),
            GET_LOCATION_TIMEOUT=get_env_or_default("GET_LOCATION_TIMEOUT", 10),
            PROXIES={"http": "", "https": ""},
        )


config = AppConfig.load()
