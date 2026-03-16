import logging

from PyQt6.QtCore import QObject, pyqtSignal


class LogSignaler(QObject):
    log_received = pyqtSignal(str)


class QtLogHandler(logging.Handler):
    def __init__(self, signaler: LogSignaler) -> None:
        super().__init__()
        self.signaler = signaler
        self.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        self.signaler.log_received.emit(msg)
