# csust-login-script

`csust-login-script` 是一个用于长沙理工大学校园网登录的 Python 项目。本项目适配 2025 年上半年学校的新登录系统。

## 环境要求

- 安装相关依赖：
  ```bash
  pip install -r requirements.txt
  ```

## 使用方法

### 1. 配置环境变量

你需要配置以下环境变量：

- `CSUST_USERNAME`: 你的校园网账号
- `CSUST_PASSWORD`: 你的校园网密码

可以使用`.env`文件来配置环境变量

### 2. 启动脚本

运行主脚本 `login.py` 来开始自动登录过程：

```bash
python login.py
```

## 配置说明

### 定时模式

在启用 CNN 验证码识别的基础上，还需额外配置环境变量：

- `DAEMON_EXEC_INTERVAL`：守护进程定时执行主脚本的间隔（单位为秒，默认为 `20`）。

配置后，运行守护进程 `daemon.py` 并保持后台运行即可定时检查登录状态并自动尝试登录。

```bash
python daemon.py
```
