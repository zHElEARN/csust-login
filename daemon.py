import threading
import time

import schedule

import login
from config import config
from logger import get_logger

logger = get_logger("daemon")

login_lock = threading.Lock()


# 定义定时任务函数，根据配置设置执行间隔
@schedule.repeat(schedule.every(config.DAEMON_EXEC_INTERVAL).seconds)
def run_login_script():
    if not login_lock.acquire(blocking=False):
        logger.warning("daemon: 上一个任务还未完成，跳过本次执行")
        return
    try:
        if login.is_online():
            logger.info("daemon: 网络连接正常，无需进行登录")
        else:
            logger.info("daemon: 准备进行登录")
            login.main()
    finally:
        login_lock.release()


def main():
    schedule.run_all()
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    exit(main())
