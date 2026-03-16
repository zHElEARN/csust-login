import json
import re
import sys
from typing import Any
from urllib.parse import parse_qs, urlparse

import requests

from .config import config
from .logger import get_logger
from .utils import is_online

logger = get_logger("login")


class LoginSession:
    def __init__(self) -> None:
        self._session = requests.Session()

    def login(self, username: str, password: str, location_params: dict[str, str]) -> tuple[bool, str]:
        """
        执行登录操作
        :return: (是否成功, 响应信息或错误原因)
        """
        params = {
            "callback": "dr1004",
            "login_method": 1,
            "user_account": f",0,{username}",
            "user_password": password,
            "wlan_user_ip": location_params.get("wlanuserip", ""),
            "wlan_user_mac": location_params.get("wlanusermac", ""),
            "wlan_ac_ip": location_params.get("wlanacip", ""),
            "wlan_ac_name": location_params.get("wlanacname", ""),
            "jsVersion": "4.2.1",
            "terminal_type": 1,
            "lang": "zh",
            "v": 3333,
        }

        try:
            response = self._session.get(
                "https://login.csust.edu.cn:802/eportal/portal/login",
                params=params,
                proxies=config.PROXIES,
                verify=False,
                timeout=config.LOGIN_TIMEOUT,
            )
            response.raise_for_status()
            data = self._parse_callback(response.text)
        except requests.RequestException as e:
            return False, f"网络请求失败: {e}"
        except ValueError as e:
            return False, f"数据解析失败: {e}"

        return data.get("result") == 1, data.get("msg", "未知错误")

    @staticmethod
    def _parse_callback(text: str) -> dict[str, Any]:
        """解析回调函数响应"""
        match = re.match(r"^\w+\((.*)\);$", text.strip())
        if not match:
            raise ValueError("无效的响应格式")
        return json.loads(match.group(1))

    @staticmethod
    def get_location_parameters() -> tuple[dict[str, str] | None, str]:
        """
        获取重定向地址中的查询参数
        :return: (参数字典, 错误信息)，如果成功则错误信息为空字符串
        """
        try:
            response = requests.get("http://10.10.10.10/", allow_redirects=False, proxies=config.PROXIES, timeout=config.GET_LOCATION_TIMEOUT)
            response.raise_for_status()
        except requests.RequestException as e:
            return None, f"请求重定向地址失败: {e}"

        location = response.headers.get("Location", "")
        if not location:
            return None, "响应头中未找到 Location 字段"

        parsed = urlparse(location)
        params = {k: v[0] for k, v in parse_qs(parsed.query).items()}
        return params, ""


def login() -> bool:
    try:
        while True:
            session = LoginSession()

            location_params, err_msg = session.get_location_parameters()
            if location_params is None:
                logger.error(f"无法获取网络位置参数: {err_msg}")
                return False

            # 登录流程
            success, msg = session.login(config.USERNAME, config.PASSWORD, location_params)
            if success:
                logger.info("校园网登录成功")
                return True

            # 处理需要重新登录的情况
            if "login again" in msg.lower():
                logger.warning("检测到需要重新登录，重启登录流程...")
                continue  # 继续外部循环

            logger.error(f"登录失败: {msg}")
            return False

    except Exception as e:
        logger.error(f"程序执行异常: {e}")
        return False


if __name__ == "__main__":
    if is_online():
        logger.info("当前已检测到网络连接，无需登录")
        sys.exit(0)
    else:
        sys.exit(0 if login() else 1)
