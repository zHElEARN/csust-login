import os
import sys

from PyQt6.QtGui import QCloseEvent, QFontDatabase, QIcon
from PyQt6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from csust_login.config import AppConfig, config
from csust_login.logger import setup_ui_logging
from csust_login.ui.config_path import get_ui_config_path
from csust_login.ui.logger import LogSignaler, QtLogHandler
from csust_login.ui.worker import DaemonWorker


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.app_config = AppConfig.load_from_file(get_ui_config_path())
        # 加载配置
        self.setWindowTitle("CSUST Login")
        self._set_window_icon()
        self.setMinimumSize(520, 620)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 12, 12, 12)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self._init_control_tab()
        self._init_advanced_tab()
        self._setup_logging()

        # 初始填充数据
        self._load_config_to_ui()

        self.worker = None

    def _set_window_icon(self) -> None:
        """设置窗口图标"""
        try:
            if getattr(sys, "frozen", False):
                # PyInstaller 运行环境
                base_dir = getattr(sys, "_MEIPASS")
            else:
                # 正常 Python 运行环境
                ui_dir = os.path.dirname(os.path.abspath(__file__))
                base_dir = os.path.dirname(ui_dir)

            icon_path = os.path.join(base_dir, "resources", "icons", "app_icon.png")
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
        except Exception:
            pass

    def _setup_logging(self) -> None:
        self.log_signaler = LogSignaler()
        self.log_signaler.log_received.connect(self._append_log)
        self.log_handler = QtLogHandler(self.log_signaler)
        setup_ui_logging(self.log_handler)

    def closeEvent(self, a0: QCloseEvent | None) -> None:
        """窗口关闭时停止守护进程"""
        self._stop_daemon()
        if self.worker and self.worker.isRunning():
            self.worker.wait()
        if a0:
            a0.accept()

    def _append_log(self, message: str) -> None:
        self.log_output.append(message)
        # 自动滚动到底部
        self.log_output.moveCursor(self.log_output.textCursor().MoveOperation.End)

    def _init_control_tab(self) -> None:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        # 账号信息
        account_group = QGroupBox("账号信息")
        account_layout = QFormLayout(account_group)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入校园网账号")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入校园网密码")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        account_layout.addRow("用户名:", self.username_input)
        account_layout.addRow("密码:", self.password_input)
        layout.addWidget(account_group)

        # 守护进程设置
        daemon_group = QGroupBox("守护进程设置")
        daemon_layout = QFormLayout(daemon_group)
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(5, 3600)
        self.interval_spin.setSuffix(" 秒")
        self.retry_spin = QSpinBox()
        self.retry_spin.setRange(1, 300)
        self.retry_spin.setSuffix(" 秒")
        daemon_layout.addRow("检测间隔:", self.interval_spin)
        daemon_layout.addRow("重试间隔:", self.retry_spin)
        layout.addWidget(daemon_group)

        # 按钮区域
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("开启自动登录")
        self.start_button.clicked.connect(self._start_daemon)
        self.stop_button = QPushButton("停止自动登录")
        self.stop_button.clicked.connect(self._stop_daemon)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        layout.addLayout(button_layout)

        # 状态栏
        status_layout = QHBoxLayout()
        self.status_indicator = QLabel("未运行")
        self.status_indicator.setStyleSheet("color: gray; font-weight: bold;")
        status_layout.addWidget(QLabel("当前状态:"))
        status_layout.addWidget(self.status_indicator)
        status_layout.addStretch()
        layout.addLayout(status_layout)

        # 运行日志
        log_group = QGroupBox("运行日志")
        log_layout = QVBoxLayout(log_group)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
        self.log_output.setPlaceholderText("日志信息将在此处显示...")
        log_layout.addWidget(self.log_output)
        layout.addWidget(log_group, stretch=1)

        self.tabs.addTab(tab, "控制面板")

    def _init_advanced_tab(self) -> None:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        # 网络与超时
        timeout_group = QGroupBox("网络与超时配置")
        timeout_layout = QFormLayout(timeout_group)
        self.check_timeout_spin = QSpinBox()
        self.check_timeout_spin.setRange(1, 60)
        self.login_timeout_spin = QSpinBox()
        self.login_timeout_spin.setRange(1, 60)
        timeout_layout.addRow("网络检测超时 (秒):", self.check_timeout_spin)
        timeout_layout.addRow("登录请求超时 (秒):", self.login_timeout_spin)
        layout.addWidget(timeout_group)

        # 网络重置设置
        reset_group = QGroupBox("网络重置配置")
        reset_layout = QFormLayout(reset_group)
        self.reset_cmd_input = QTextEdit()
        self.reset_cmd_input.setPlaceholderText("例如: networksetup -setairportpower en0 off && sleep 1 && networksetup -setairportpower en0 on")
        self.reset_cmd_input.setMaximumHeight(80)
        self.reset_timeout_spin = QSpinBox()
        self.reset_timeout_spin.setRange(1, 120)
        self.reset_wait_spin = QSpinBox()
        self.reset_wait_spin.setRange(1, 60)
        reset_layout.addRow("网络重置命令:", self.reset_cmd_input)
        reset_layout.addRow("命令执行超时 (秒):", self.reset_timeout_spin)
        reset_layout.addRow("重置后等待 (秒):", self.reset_wait_spin)
        layout.addWidget(reset_group)

        # 日志配置
        log_config_group = QGroupBox("日志配置")
        log_config_layout = QFormLayout(log_config_group)

        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])

        log_config_layout.addRow("日志级别:", self.log_level_combo)
        layout.addWidget(log_config_group)

        layout.addStretch()
        self.tabs.addTab(tab, "高级配置")

    def _load_config_to_ui(self) -> None:
        self.username_input.setText(self.app_config.USERNAME)
        self.password_input.setText(self.app_config.PASSWORD)
        self.interval_spin.setValue(self.app_config.DAEMON_EXEC_INTERVAL)
        self.retry_spin.setValue(self.app_config.DAEMON_RETRY_INTERVAL)
        self.check_timeout_spin.setValue(self.app_config.CHECK_NETWORK_TIMEOUT)
        self.login_timeout_spin.setValue(self.app_config.LOGIN_TIMEOUT)
        self.reset_cmd_input.setPlainText(self.app_config.NETWORK_RESET_CMD)
        self.reset_timeout_spin.setValue(self.app_config.NETWORK_RESET_TIMEOUT)
        self.reset_wait_spin.setValue(self.app_config.NETWORK_RESET_WAIT)
        self.log_level_combo.setCurrentText(self.app_config.LOG_LEVEL)

    def _save_ui_to_config(self) -> None:
        self.app_config.USERNAME = self.username_input.text()
        self.app_config.PASSWORD = self.password_input.text()
        self.app_config.DAEMON_EXEC_INTERVAL = self.interval_spin.value()
        self.app_config.DAEMON_RETRY_INTERVAL = self.retry_spin.value()
        self.app_config.CHECK_NETWORK_TIMEOUT = self.check_timeout_spin.value()
        self.app_config.LOGIN_TIMEOUT = self.login_timeout_spin.value()
        self.app_config.NETWORK_RESET_CMD = self.reset_cmd_input.toPlainText().strip()
        self.app_config.NETWORK_RESET_TIMEOUT = self.reset_timeout_spin.value()
        self.app_config.NETWORK_RESET_WAIT = self.reset_wait_spin.value()
        self.app_config.LOG_LEVEL = self.log_level_combo.currentText()

        config.update_from(self.app_config)

        self.app_config.save(get_ui_config_path())

    def _toggle_inputs(self, enabled: bool) -> None:
        """启用或禁用所有配置输入项"""
        widgets = [
            self.username_input,
            self.password_input,
            self.interval_spin,
            self.retry_spin,
            self.check_timeout_spin,
            self.login_timeout_spin,
            self.reset_cmd_input,
            self.reset_timeout_spin,
            self.reset_wait_spin,
            self.log_level_combo,
        ]
        for widget in widgets:
            widget.setEnabled(enabled)

    def _start_daemon(self) -> None:
        self._save_ui_to_config()
        if not self.app_config.USERNAME or not self.app_config.PASSWORD:
            self._append_log("错误: 用户名或密码不能为空！")
            return

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self._toggle_inputs(False)
        self.status_indicator.setText("正在运行")
        self.status_indicator.setStyleSheet("color: green; font-weight: bold;")

        self.worker = DaemonWorker(self.app_config)
        self.worker.status_changed.connect(self._on_status_changed)
        self.worker.start()

    def _stop_daemon(self) -> None:
        if self.worker:
            self.worker.stop()

    def _on_status_changed(self, status: str) -> None:
        self.status_indicator.setText(status)
        if status == "已停止":
            self.status_indicator.setStyleSheet("color: gray; font-weight: bold;")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self._toggle_inputs(True)
        elif status == "正在运行":
            self.status_indicator.setStyleSheet("color: green; font-weight: bold;")
            self._toggle_inputs(False)
