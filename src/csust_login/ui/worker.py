import subprocess
import time

from notifypy import Notify
from PyQt6.QtCore import QThread, pyqtSignal

from csust_login.config import AppConfig
from csust_login.logger import get_logger
from csust_login.login import login
from csust_login.utils import check_network_status


class DaemonWorker(QThread):
    finished = pyqtSignal()
    status_changed = pyqtSignal(str)

    def __init__(self, app_config: AppConfig) -> None:
        super().__init__()
        self.config = app_config
        self.running = True
        self.logger = get_logger("ui_daemon")

    def stop(self) -> None:
        self.running = False

    def notify(self, title: str, message: str) -> None:
        """发送系统通知"""
        try:
            notification = Notify()
            notification.title = title
            notification.message = message
            notification.application_name = "CSUST Login"
            notification.send()
        except Exception as e:
            self.logger.error(f"发送通知失败: {e}")

    def run(self) -> None:
        self.logger.info(f"守护进程已启动，正常检测间隔: {self.config.DAEMON_EXEC_INTERVAL} 秒")
        self.status_changed.emit("正在运行")

        while self.running:
            try:
                is_online, location_params = check_network_status()

                if is_online:
                    self.logger.info("网络正常，无需登录")
                    self._sleep(self.config.DAEMON_EXEC_INTERVAL)
                else:
                    self.logger.info("检测到离线，准备进行登录...")
                    self.notify("检测到离线", "检测到离线，准备进行登录...")
                    if location_params:
                        self.logger.info("检测到离线并成功拦截重定向参数，准备进行登录...")
                        success = login(location_params)

                        if success:
                            self.logger.info("后台登录成功，恢复常规间隔检测")
                            self.notify("登录成功", "校园网自动登录成功")
                            self._sleep(self.config.DAEMON_EXEC_INTERVAL)
                        else:
                            self.logger.error("后台登录失败，即将重新尝试...")
                            self.notify("登录失败", "校园网自动登录失败，即将重试")
                            self._sleep(self.config.DAEMON_RETRY_INTERVAL)
                    else:
                        self.logger.warning("未能获取到网关参数，可能物理断网或 Wi-Fi 已断开。")

                        if self.config.NETWORK_RESET_CMD:
                            self.logger.info(f"正在执行网络重置命令: {self.config.NETWORK_RESET_CMD}")
                            self.notify("网络重置", "执行网络重置命令，等待恢复")
                            try:
                                subprocess.run(
                                    self.config.NETWORK_RESET_CMD,
                                    shell=True,
                                    check=True,
                                    timeout=self.config.NETWORK_RESET_TIMEOUT,
                                    capture_output=True,
                                    text=True,
                                )
                                self.logger.info(f"网络重置命令执行完毕，等待 {self.config.NETWORK_RESET_WAIT} 秒让网络接口恢复...")
                                self._sleep(self.config.NETWORK_RESET_WAIT)
                            except subprocess.TimeoutExpired:
                                self.logger.error(f"网络重置命令执行超时 ({self.config.NETWORK_RESET_TIMEOUT}秒)")
                            except subprocess.CalledProcessError as e:
                                self.logger.error(f"网络重置命令执行失败，退出码: {e.returncode}, 错误信息: {e.stderr.strip()}")
                            except Exception as e:
                                self.logger.error(f"执行自定义命令时发生未知异常: {e}")
                        else:
                            self.logger.info("未配置网络重置命令，等待下一次检测...")
                            self.notify("离线状态", "未配置网络重置命令，等待下一次检测...")

                        self._sleep(self.config.DAEMON_RETRY_INTERVAL)

            except Exception as e:
                self.logger.error(f"守护进程任务发生异常: {e}")
                self._sleep(self.config.DAEMON_RETRY_INTERVAL)

        self.status_changed.emit("已停止")
        self.finished.emit()

    def _sleep(self, seconds: int) -> None:
        """可中断的休眠"""
        for _ in range(seconds * 10):
            if not self.running:
                break
            time.sleep(0.1)
