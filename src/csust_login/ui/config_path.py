import os
import sys

_APP_NAME = "csust-login"
_CONFIG_FILENAME = "config.yaml"


def get_ui_config_path() -> str:
    if sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")
    elif sys.platform == "win32":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
    else:
        base = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))

    config_dir = os.path.join(base, _APP_NAME)
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, _CONFIG_FILENAME)
