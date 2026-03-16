import sys
import time

from .config import config
from .logger import get_logger
from .login import login
from .utils import is_online

logger = get_logger("daemon")


def start_daemon() -> None:
    """启动守护进程"""
    logger.info(f"守护进程已启动，正常检测间隔: {config.DAEMON_EXEC_INTERVAL} 秒")

    while True:
        try:
            if is_online():
                logger.info("网络正常，无需登录")
                time.sleep(config.DAEMON_EXEC_INTERVAL)
            else:
                logger.info("检测到离线，准备进行登录...")
                success = login()

                if success:
                    logger.info("后台登录成功，恢复常规间隔检测")
                    time.sleep(config.DAEMON_EXEC_INTERVAL)
                else:
                    logger.error("后台登录失败，即将重新尝试登录...")
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
