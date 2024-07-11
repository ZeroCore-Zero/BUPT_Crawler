import logging
import time
import os


class MyLogger():
    def __init__(self, name):
        # 预处理变量
        self.today = time.strftime("%Y-%m-%d")
        self.log_path = os.path.join(os.path.dirname(__file__), "../log")
        if not os.path.exists(self.log_path):
            os.mkdir(self.log_path)

        # 生成日志记录器
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
        if os.path.exists(os.path.join(self.log_path, f"{self.today}.log")):
            self.file_handler = logging.FileHandler(filename=os.path.join(self.log_path, f"{self.today}.log"))
        else:
            self.file_handler = logging.FileHandler(filename=os.path.join(self.log_path, "lastest.log"))
        self.file_handler.setLevel(logging.DEBUG)
        self.file_handler.setFormatter(self.log_formatter)
        self.log.addHandler(self.file_handler)

    def _checkDate(self):
        """ 如果是新的一天则重新记录到新的文件 """
        today = time.strftime("%Y-%m-%d")
        if today == self.today:
            return
        self.log.removeHandler(self.file_handler)
        self.file_handler.close()
        time.sleep(3)
        os.rename(
            os.path.join(self.log_path, "lastest.log"),
            os.path.join(self.log_path, f"{self.today}.log")
        )
        self.today = today
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
