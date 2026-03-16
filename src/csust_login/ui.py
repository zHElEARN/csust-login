import sys

from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
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


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("长沙理工大学校园网自动登录")
        self.setMinimumSize(520, 620)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 12, 12, 12)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self._init_control_tab()
        self._init_advanced_tab()

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
        self.interval_spin.setValue(20)
        self.retry_spin = QSpinBox()
        self.retry_spin.setRange(1, 300)
        self.retry_spin.setValue(3)
        daemon_layout.addRow("检测间隔 (秒):", self.interval_spin)
        daemon_layout.addRow("重试间隔 (秒):", self.retry_spin)
        layout.addWidget(daemon_group)

        # 按钮区域
        button_layout = QHBoxLayout()
        self.daemon_button = QPushButton("开启自动登录")
        self.stop_button = QPushButton("停止自动登录")
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.daemon_button)
        button_layout.addWidget(self.stop_button)
        layout.addLayout(button_layout)

        # 状态栏
        status_layout = QHBoxLayout()
        self.status_indicator = QLabel("未运行")
        status_layout.addWidget(QLabel("当前状态:"))
        status_layout.addWidget(self.status_indicator)
        status_layout.addStretch()
        layout.addLayout(status_layout)

        # 运行日志
        log_group = QGroupBox("运行日志")
        log_layout = QVBoxLayout(log_group)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        # 使用系统等宽字体
        self.log_output.setPlaceholderText("日志信息将在此处显示...")
        log_layout.addWidget(self.log_output)
        layout.addWidget(log_group, stretch=1)

        self.tabs.addTab(tab, "控制面板")

    def _init_advanced_tab(self) -> None:
        """初始化高级配置面板"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        # 网络与超时
        timeout_group = QGroupBox("网络与超时配置")
        timeout_layout = QFormLayout(timeout_group)
        self.check_timeout_spin = QSpinBox()
        self.check_timeout_spin.setValue(5)
        self.login_timeout_spin = QSpinBox()
        self.login_timeout_spin.setValue(10)
        timeout_layout.addRow("网络检测超时 (秒):", self.check_timeout_spin)
        timeout_layout.addRow("登录请求超时 (秒):", self.login_timeout_spin)
        layout.addWidget(timeout_group)

        # 网络重置设置
        reset_group = QGroupBox("网络重置配置")
        reset_layout = QFormLayout(reset_group)
        self.reset_cmd_input = QTextEdit()
        self.reset_cmd_input.setPlaceholderText("留空则不执行")
        self.reset_cmd_input.setMaximumHeight(80)
        self.reset_timeout_spin = QSpinBox()
        self.reset_timeout_spin.setRange(1, 120)
        self.reset_timeout_spin.setValue(20)
        self.reset_wait_spin = QSpinBox()
        self.reset_wait_spin.setRange(1, 60)
        self.reset_wait_spin.setValue(5)
        reset_layout.addRow("网络重置命令:", self.reset_cmd_input)
        reset_layout.addRow("命令执行超时 (秒):", self.reset_timeout_spin)
        reset_layout.addRow("重置后等待 (秒):", self.reset_wait_spin)
        layout.addWidget(reset_group)

        # 日志配置
        log_config_group = QGroupBox("日志配置")
        log_config_layout = QFormLayout(log_config_group)

        self.enable_log_check = QCheckBox("启用本地文件日志记录")
        self.enable_log_check.setChecked(True)

        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_combo.setCurrentText("INFO")

        self.log_path_input = QLineEdit()
        self.log_path_input.setPlaceholderText("日志文件保存目录，默认为 logs")
        self.log_path_input.setText("logs")

        log_config_layout.addRow("开启日志:", self.enable_log_check)
        log_config_layout.addRow("日志级别:", self.log_level_combo)
        log_config_layout.addRow("日志路径:", self.log_path_input)
        layout.addWidget(log_config_group)

        layout.addStretch()
        self.tabs.addTab(tab, "高级配置")


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
