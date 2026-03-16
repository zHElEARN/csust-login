import json
import re
import sys
from typing import Any

import requests

from .config import config
from .logger import get_logger
from .utils import check_network_status, resolve_domain

logger = get_logger("login")


class LoginSession:
    def __init__(self) -> None:
        self._session = requests.Session()

    def login(self, username: str, password: str, location_params: dict[str, str]) -> tuple[bool, str]:
        """
        执行登录操作
        :return: (是否成功, 响应信息或错误原因)
        """

        domain = "login.csust.edu.cn"
        dns_server = "10.255.255.25"
        fallback_ip = "192.168.7.221"

        target_ip = resolve_domain(domain, dns_server)
        if target_ip:
            logger.info(f"通过自定义 DNS ({dns_server}) 成功解析 {domain} -> {target_ip}")
        else:
            target_ip = fallback_ip
            logger.warning(f"自定义 DNS 解析失败，将使用备用 IP: {fallback_ip}")

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

        headers = {"Host": f"{domain}:802"}
        target_url = f"https://{target_ip}:802/eportal/portal/login"

        try:
            response = self._session.get(
                target_url,
                headers=headers,
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


def login(location_params: dict[str, str]) -> bool:
    try:
        while True:
            session = LoginSession()

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


def main():
    if not config.USERNAME or not config.PASSWORD:
        logger.error("必须设置环境变量 CSUST_USERNAME 和 CSUST_PASSWORD")
        sys.exit(1)

    is_online, location_params = check_network_status()

    if is_online:
        logger.info("当前已检测到网络连接，无需登录")
        sys.exit(0)
    elif location_params:
        sys.exit(0 if login(location_params) else 1)
    else:
        logger.error("未连接网络，且无法获取登录重定向参数")
        sys.exit(1)


if __name__ == "__main__":
    main()
