import sys
import threading
import time

import schedule

from . import login as login_module
from .config import config
from .logger import get_logger
from .utils import is_online

logger = get_logger("daemon")

login_lock = threading.Lock()


def run_login_task() -> None:
    if not login_lock.acquire(blocking=False):
        logger.warning("上一个任务还未完成，跳过本次执行")
        return

    try:
        if is_online():
            logger.info("网络连接正常，无需进行登录")
        else:
            logger.info("检测到离线，准备进行登录...")
            exit_code = login_module.login()
            if exit_code != 0:
                logger.error("后台登录任务执行失败")
    except Exception as e:
        logger.error(f"守护进程任务发生异常: {e}")
    finally:
        login_lock.release()


def start_daemon() -> None:
    """启动守护进程调度"""
    logger.info(f"守护进程已启动，执行间隔: {config.DAEMON_EXEC_INTERVAL} 秒")
    schedule.every(config.DAEMON_EXEC_INTERVAL).seconds.do(run_login_task)

    schedule.run_all()
    while True:
        schedule.run_pending()
        time.sleep(1)


def main():
    try:
        start_daemon()
    except KeyboardInterrupt:
        logger.info("守护进程已被手动停止")
        sys.exit(0)


if __name__ == "__main__":
    main()
