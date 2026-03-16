import dns.resolver
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
