import logging
import time
import os


def getLogger(name):
    # Config logging
    today = time.strftime("%Y-%m-%d", time.localtime())
    log_path = os.path.join(os.path.dirname(__file__), "../log")
    if not os.path.exists(log_path):
        os.mkdir(log_path)

    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    log_formatter = logging.Formatter(
        fmt="%(asctime)s %(name)s:%(levelname)s:%(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    # log to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_formatter)
    log.addHandler(console_handler)

    # log to file
    file_handler = logging.FileHandler(filename=os.path.join(log_path, f"{today}.log"))
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_formatter)
    log.addHandler(file_handler)

    return log
