import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from qt_material import apply_stylesheet

from csust_login.ui.main_window import MainWindow


def _get_theme_by_system_mode(app: QApplication) -> str:
    style_hints = app.styleHints()
    if style_hints is None:
        return "light_blue.xml"

    scheme = style_hints.colorScheme()
    if scheme == Qt.ColorScheme.Dark:
        return "dark_blue.xml"
    return "light_blue.xml"


def _apply_theme_by_system_mode(app: QApplication) -> None:
    apply_stylesheet(app, theme=_get_theme_by_system_mode(app))


def main() -> None:
    app = QApplication(sys.argv)
    _apply_theme_by_system_mode(app)
    style_hints = app.styleHints()
    if style_hints is not None:
        style_hints.colorSchemeChanged.connect(lambda _: _apply_theme_by_system_mode(app))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
