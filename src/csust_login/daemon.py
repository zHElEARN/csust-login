import subprocess
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
                    logger.warning("未能获取到网关参数，可能物理断网或 Wi-Fi 已断开。")

                    if config.NETWORK_RESET_CMD:
                        logger.info(f"正在执行网络重置命令: {config.NETWORK_RESET_CMD}")
                        try:
                            subprocess.run(
                                config.NETWORK_RESET_CMD,
                                shell=True,
                                check=True,
                                timeout=config.NETWORK_RESET_TIMEOUT,
                                capture_output=True,
                                text=True,
                            )
                            logger.info(f"网络重置命令执行完毕，等待 {config.NETWORK_RESET_WAIT} 秒让网络接口恢复...")
                            time.sleep(config.NETWORK_RESET_WAIT)
                        except subprocess.TimeoutExpired:
                            logger.error(f"网络重置命令执行超时 ({config.NETWORK_RESET_TIMEOUT}秒)")
                        except subprocess.CalledProcessError as e:
                            logger.error(f"网络重置命令执行失败，退出码: {e.returncode}, 错误信息: {e.stderr.strip()}")
                        except Exception as e:
                            logger.error(f"执行自定义命令时发生未知异常: {e}")

                    time.sleep(config.DAEMON_RETRY_INTERVAL)

        except Exception as e:
            logger.error(f"守护进程任务发生异常: {e}")
            time.sleep(config.DAEMON_RETRY_INTERVAL)


def main():
    if not config.USERNAME or not config.PASSWORD:
        logger.error("必须设置环境变量 CSUST_USERNAME 和 CSUST_PASSWORD")
        sys.exit(1)

    try:
        start_daemon()
    except KeyboardInterrupt:
        logger.info("守护进程已被手动停止")
        sys.exit(0)


if __name__ == "__main__":
    main()
