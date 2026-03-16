import requests

from .config import config


def is_online() -> bool:
    """检测当前网络状态"""
    try:
        response = requests.get(
            "http://connect.rom.miui.com/generate_204",
            proxies=config.PROXIES,
            timeout=config.CHECK_NETWORK_TIMEOUT,
        )
        return response.status_code == 204
    except requests.RequestException:
        return False
