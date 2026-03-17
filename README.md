# csust-login

这是一个用于自动登录长沙理工大学校园网的 Python 脚本工具。该工具能够自动检测网络连接状态，并在掉线时自动进行登录。

## 安装说明

你可以通过 Python 的包管理器 `pip` 安装此工具。根据你的使用场景，有以下两种安装方式：

### 基础安装

如果你只需要**命令行**功能（例如在 Linux 服务器、OpenWrt 路由器上实现自动静默登录），请执行：

```bash
pip install csust-login
```

### 完整安装

如果你在 Windows 或 macOS 电脑上使用，并希望拥有**图形化界面（App 界面）**和**系统通知**功能，推荐安装 UI 扩展部分：

```bash
pip install "csust-login[ui]"
```

## 使用方法（命令行模式）

命令行模式非常适合在服务器、路由器或不需要图形界面的环境下长时间运行。

### 1. 准备配置文件

在使用之前，你需要在程序运行的目录下创建一个名为 `config.yaml` 的文件，用于存放你的校园网账号信息。

**最简配置示例：**
只需填入你的学号和密码即可。

```yaml
USERNAME: "你的学号"
PASSWORD: "你的密码"
```

<details>
<summary>点击查看完整配置项（进阶用户）</summary>

如果你有特殊需求（如修改检测频率或设置网络重置命令），可以参考以下完整字段：

```yaml
USERNAME: "" # 学号
PASSWORD: "" # 密码
DAEMON_EXEC_INTERVAL: 20 # 守护进程正常检测间隔（秒）
DAEMON_RETRY_INTERVAL: 3 # 登录失败后的重试间隔（秒）
CHECK_NETWORK_TIMEOUT: 5 # 网络检查超时时间
LOGIN_TIMEOUT: 10 # 登录请求超时时间
ENABLE_LOGGING: true # 是否开启日志记录
LOG_DIR: "logs" # 日志存放目录
LOG_LEVEL: "INFO" # 日志级别
NETWORK_RESET_CMD: "" # 网络重置自定义命令（例如重启网卡）
```

</details>

### 2. 运行工具

安装完成后，你可以直接在终端使用以下两个命令：

#### **手动单次登录**

用于立即执行一次登录检查。如果已在线则跳过，如果离线则尝试登录。

```bash
csust-login
```

#### **后台守护进程**

用于自动巡检。程序会根据配置的间隔时间（默认 20 秒）自动检测网络状态，发现掉线自动重连。

```bash
csust-login-daemon
```

## 使用方法（图形界面模式）

如果你已通过 `pip install "csust-login[ui]"` 安装了 UI 扩展，可以直接在终端运行：

```bash
csust-login-ui
```

启动后会打开图形界面窗口，你可以在界面中直接配置账号、密码等参数，无需手动编辑配置文件。
