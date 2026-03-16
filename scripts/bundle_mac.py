import os
import subprocess


def build():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)

    print(f"正在项目根目录构建: {project_root}")

    main_script = os.path.join("src", "csust_login", "ui", "__main__.py")
    resources_src = os.path.join("src", "csust_login", "resources")
    icon_file = os.path.join("src", "csust_login", "resources", "icons", "app_icon.icns")

    # 构建命令
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--windowed",
        "--name=CSUST-Login",
        f"--icon={icon_file}",
        f"--add-data={resources_src}:resources",
        "--clean",
        main_script,
    ]

    print("执行命令:", " ".join(cmd))

    try:
        subprocess.run(cmd, check=True)
        print("\n构建成功")
        print("打包结果位于 dist/CSUST-Login.app")
    except subprocess.CalledProcessError as e:
        print(f"\n构建失败: {e}")
    except FileNotFoundError:
        print("\n错误: 未找到 pyinstaller 命令。请先安装: pip install pyinstaller")


if __name__ == "__main__":
    build()
