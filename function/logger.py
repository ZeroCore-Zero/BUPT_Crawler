import logging
import time
import os


class MyLogger():
    def __init__(self, name):
        self.today = time.strftime("%Y-%m-%d", time.localtime())
        self.log_path = os.path.join(os.path.dirname(__file__), "../log")
        if not os.path.exists(self.log_path):
            os.mkdir(self.log_path)

        self.log = logging.getLogger(name)
        self.log.setLevel(logging.DEBUG)
        self.log_formatter = logging.Formatter(
            fmt="%(asctime)s %(name)s:%(levelname)s:%(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        # log to console
        self.console_handler = logging.StreamHandler()
        self.console_handler.setLevel(logging.INFO)
        self.console_handler.setFormatter(self.log_formatter)
        self.log.addHandler(self.console_handler)

        # log to file
        self.file_handler = logging.FileHandler(filename=os.path.join(self.log_path, f"{self.today}.log"))
        self.file_handler.setLevel(logging.DEBUG)
        self.file_handler.setFormatter(self.log_formatter)
        self.log.addHandler(self.file_handler)

    def _checkDate(self):
        today = time.strftime("%Y-%m-%d", time.localtime())
        if today == self.today:
            return
        self.today = today
        self.log.removeHandler(self.file_handler)
        self.file_handler.close()
        self.file_handler = logging.FileHandler(filename=os.path.join(self.log_path, f"{self.today}.log"))
        self.file_handler.setLevel(logging.DEBUG)
        self.file_handler.setFormatter(self.log_formatter)
        self.log.addHandler(self.file_handler)

    def debug(self, str):
        self._checkDate()
        self.log.debug(str)

    def info(self, str):
        self._checkDate()
        self.log.info(str)

    def warning(self, str):
        self._checkDate()
        self.log.warning(str)

    def error(self, str):
        self._checkDate()
        self.log.error(str)

    def critical(self, str):
        self._checkDate()
        self.log.critical(str)


def getLogger(name):
    return MyLogger(name)
