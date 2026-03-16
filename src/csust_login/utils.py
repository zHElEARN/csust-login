from urllib.parse import parse_qs, urlparse

import dns.resolver
import requests

from .config import config


def check_network_status() -> tuple[bool, dict[str, str] | None]:
    """
    检测网络状态并获取可能存在的重定向参数。
    :return: (是否在线, 重定向参数字典)
            如果在线，返回 (True, None)
            如果离线且被劫持，返回 (False, params)
            如果离线但未获取到参数（如彻底断网），返回 (False, None)
    """
    try:
        response = requests.get(
            "http://connect.rom.miui.com/generate_204",
            allow_redirects=False,
            proxies=config.PROXIES,
            timeout=config.CHECK_NETWORK_TIMEOUT,
        )

        # 正常连通外网
        if response.status_code == 204:
            return True, None

        # 被校园网网关劫持
        if response.status_code in (301, 302, 303, 307):
            location = response.headers.get("Location", "")
            if location:
                parsed = urlparse(location)
                params = {k: v[0] for k, v in parse_qs(parsed.query).items()}
                return False, params

        return False, None
    except requests.RequestException:
        # 请求异常（如 Wi-Fi 断开没有 IP）
        return False, None


def resolve_domain(domain: str, dns_server: str = "10.255.255.25", timeout: float = 3.0) -> str | None:
    """
    使用指定的 DNS 服务器解析域名
    """
    try:
        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = [dns_server]
        resolver.lifetime = timeout
        answers = resolver.resolve(domain, "A")
        if answers:
            return str(answers[0])
    except Exception:
        pass

    return None
