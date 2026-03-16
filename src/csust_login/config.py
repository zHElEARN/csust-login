import os
from dataclasses import asdict, dataclass, fields

import urllib3
import yaml

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEFAULT_CONFIG_PATH = "config.yaml"


def _get_default_config() -> "AppConfig":
    """获取程序默认配置项"""
    return AppConfig(
        USERNAME="",
        PASSWORD="",
        DAEMON_EXEC_INTERVAL=20,
        DAEMON_RETRY_INTERVAL=3,
        CHECK_NETWORK_TIMEOUT=5,
        LOGIN_TIMEOUT=10,
        NETWORK_RESET_CMD="",
        NETWORK_RESET_TIMEOUT=20,
        NETWORK_RESET_WAIT=5,
        ENABLE_LOGGING=True,
        LOG_DIR="logs",
        LOG_LEVEL="INFO",
    )


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
        """获取默认配置实例"""
        return _get_default_config()

    def update_from(self, other: "AppConfig") -> None:
        """从另一个配置对象更新当前对象的所有字段"""
        for field in fields(self):
            setattr(self, field.name, getattr(other, field.name))

    def save(self, path: str = DEFAULT_CONFIG_PATH) -> None:
        """保存配置到 YAML 文件"""
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(asdict(self), f, allow_unicode=True, sort_keys=False, indent=4)

    @classmethod
    def load_from_file(cls, path: str = DEFAULT_CONFIG_PATH) -> "AppConfig":
        """从 YAML 文件加载配置"""
        if not os.path.exists(path):
            return cls.load()

        with open(path, "r", encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError:
                return cls.load()

            if not isinstance(data, dict):
                return cls.load()

            return cls._from_dict(data)

    @classmethod
    def _from_dict(cls, data: dict) -> "AppConfig":
        """从字典创建配置对象并填充默认值"""
        field_names = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in field_names}

        default_config = _get_default_config()
        for field in fields(cls):
            if field.name not in filtered_data:
                filtered_data[field.name] = getattr(default_config, field.name)

        return cls(**filtered_data)


config = AppConfig.load_from_file()
