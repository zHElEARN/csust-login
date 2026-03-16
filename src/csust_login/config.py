import json
import os
from dataclasses import asdict, dataclass, fields
from typing import TypeVar, cast

import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

T = TypeVar("T")

DEFAULT_CONFIG_PATH = "config.json"


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

    PROXIES = {"http": "", "https": ""}

    @classmethod
    def load(cls) -> "AppConfig":
        return cls(
            USERNAME=get_env_or_default("CSUST_USERNAME", ""),
            PASSWORD=get_env_or_default("CSUST_PASSWORD", ""),
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
        )

    def save_to_json(self, path: str = DEFAULT_CONFIG_PATH) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=4, ensure_ascii=False)

    @classmethod
    def load_from_json(cls, path: str = DEFAULT_CONFIG_PATH) -> "AppConfig":
        if not os.path.exists(path):
            return cls.load()
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

            field_names = {f.name for f in fields(cls)}
            data = {k: v for k, v in data.items() if k in field_names}

            default_config = cls.load()
            for key, value in asdict(default_config).items():
                if key not in data:
                    data[key] = value
            return cls(**data)


config = AppConfig.load()
