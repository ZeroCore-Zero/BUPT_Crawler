# 通用函数
import requests
import inspect
import json
import os


def write_to_file(filename: str, text: str):
    """
        把内容写入文件，用于导出response.text

        参数：
        filename:   要写入的文件
        text:       要写入的内容
    """
    with open(filename, 'w') as file:
        file.write(text)


def sessionInit() -> requests.Session:
    """
        初始化一个requests.Session对象，清除初始header并设置UA

        返回值：
        session：   requests.Session对象
    """
    session = requests.Session()
    session.headers.clear()
    # session.headers['User-Agent']=para["ua"]
    return session


def loadData() -> tuple[dict, dict]:
    """
        载入数据，将json配置信息转换为内置字典格式

        返回值：
        config:     个人信息
        urls:       北邮网址

    """
    config_folder = os.path.join(
        os.path.dirname(__file__),
        "..",
        "config"
    )
    config_files = [
        os.path.join(config_folder, file)
        for file in os.listdir(config_folder)
    ]
    url_folder = os.path.join(
        os.path.dirname(__file__),
        "..",
        "url"
    )
    url_files = [
        os.path.join(url_folder, file)
        for file in os.listdir(url_folder)

    ]
    config = {}
    url = {}
    for config_file in config_files:
        with open(config_file, "r") as file:
            config |= json.load(file)
    for url_file in url_files:
        with open(url_file, "r") as file:
            url |= json.load(file)
    return config, url


def getCallerFile() -> str:
    """
        返回调用函数的文件地址

        返回值：
        caller_file：文件地址
    """
    caller_file = inspect.stack()[2].filename
    return caller_file
