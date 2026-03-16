import sys
import time

from .config import config
from .logger import get_logger
from .login import login
from .utils import check_network_status

logger = get_logger("daemon")


def start_daemon() -> None:
    """启动守护进程"""
    logger.info(f"守护进程已启动，正常检测间隔: {config.DAEMON_EXEC_INTERVAL} 秒")

    while True:
        try:
            is_online, location_params = check_network_status()

            if is_online:
                logger.info("网络正常，无需登录")
                time.sleep(config.DAEMON_EXEC_INTERVAL)
            else:
                if location_params:
                    logger.info("检测到离线并成功拦截重定向参数，准备进行登录...")
                    success = login(location_params)

                    if success:
                        logger.info("后台登录成功，恢复常规间隔检测")
                        time.sleep(config.DAEMON_EXEC_INTERVAL)
                    else:
                        logger.error("后台登录失败，即将重新尝试...")
                        time.sleep(config.DAEMON_RETRY_INTERVAL)
                else:
                    logger.warning("检测到离线，但未能获取到网关参数，等待重试...")
                    time.sleep(config.DAEMON_RETRY_INTERVAL)

        except Exception as e:
            logger.error(f"守护进程任务发生异常: {e}")
            time.sleep(config.DAEMON_RETRY_INTERVAL)


def main():
    try:
        start_daemon()
    except KeyboardInterrupt:
        logger.info("守护进程已被手动停止")
        sys.exit(0)


if __name__ == "__main__":
    main()
