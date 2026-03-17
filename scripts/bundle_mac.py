import glob
import os
import shutil
import stat
import subprocess

from notifypy import os_notifiers


def _format_add_data(src: str, dest: str) -> str:
    return f"{src}{os.pathsep}{dest}"


def _get_notifypy_binaries_src() -> str:
    binaries_src = os.path.join(os.path.dirname(os_notifiers.__file__), "binaries")
    notificator_app = os.path.join(binaries_src, "Notificator.app")

    if not os.path.isdir(notificator_app):
        raise RuntimeError(f"未找到 notify-py 的 Notificator.app: {notificator_app}")

    return binaries_src


def build():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)

    print(f"macOS 构建目录: {project_root}")

    main_script = os.path.join("src", "csust_login", "ui", "__main__.py")
    resources_src = os.path.join("src", "csust_login", "resources")
    icon_file = os.path.join("src", "csust_login", "resources", "icons", "app_icon.icns")
    notifypy_binaries_src = _get_notifypy_binaries_src()

    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--windowed",
        "--name=CSUST Login",
        f"--icon={icon_file}",
        f"--add-data={_format_add_data(resources_src, 'resources')}",
        f"--add-data={_format_add_data(notifypy_binaries_src, 'notifypy/os_notifiers/binaries')}",
        "--clean",
        main_script,
    ]

    print("执行:", " ".join(cmd))

    try:
        subprocess.run(cmd, check=True)
        print("构建成功，执行修复...")

        notificator_apps = glob.glob(os.path.join("dist", "**", "Notificator.app"), recursive=True)
        original_app = os.path.join(notifypy_binaries_src, "Notificator.app")

        for dest_app in notificator_apps:
            print(f"修复: {dest_app}")

            if os.path.islink(dest_app):
                os.unlink(dest_app)
            elif os.path.isdir(dest_app):
                shutil.rmtree(dest_app)
            elif os.path.exists(dest_app):
                os.remove(dest_app)

            shutil.copytree(original_app, dest_app, symlinks=False)

            applet_path = os.path.join(dest_app, "Contents", "MacOS", "applet")
            if os.path.exists(applet_path):
                st = os.stat(applet_path)
                os.chmod(applet_path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

            try:
                subprocess.run(["codesign", "--force", "--deep", "--sign", "-", dest_app], check=True, capture_output=True)
                print(f"已签名: {dest_app}")
            except subprocess.CalledProcessError as sign_err:
                print(f"签名失败: {sign_err}")

        main_app_path = os.path.join("dist", "CSUST Login.app")
        if os.path.isdir(main_app_path):
            print("签名主程序: CSUST Login.app")
            subprocess.run(["codesign", "--force", "--deep", "--sign", "-", main_app_path], capture_output=True)

        print("打包完成: dist/")

    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
    except FileNotFoundError:
        print("错误: 未找到 pyinstaller 命令")


if __name__ == "__main__":
    build()
