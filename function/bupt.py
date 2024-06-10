from bs4 import BeautifulSoup
import requests
from PIL import Image
from . import logger
import subprocess
import time
import json
import sys
import os

_MAX_RETRY = 5
log = logger.getLogger(__name__)
with open(os.path.join(os.path.dirname(__file__), "../config/bupt.json"), "r") as file:
    config = json.load(file)
with open(os.path.join(os.path.dirname(__file__), "../url/bupt.json"), "r") as file:
    url = json.load(file)


def exitProc():
    try:
        out = subprocess.run(["cat", "/var/log/syslog"], stdout=subprocess.PIPE).stdout.decode()
    except FileNotFoundError as e:
        log.error(e)
        log.error("找不到文件/var/log/syslog")
    else:
        with open(os.path.join(os.path.dirname(__file__), "../log/system.log"), "w") as file:
            file.write(out)
        log.info("系统日志/var/log/syslog已保存到文件")

    try:
        out = subprocess.run("logread", stdout=subprocess.PIPE).stdout.decode()
    except FileNotFoundError as e:
        log.error(e)
        log.error("找不到命令logread")
    else:
        with open(os.path.join(os.path.dirname(__file__), "../log/system.log"), "w") as file:
            file.write(out)
        log.info("系统日志logread已保存到文件")
    sys.exit()


def autoRetryRequest(msg, mlog, max_retry=5):
    """
        Used only for requests
    """
    def wrapper(rest, *args, **kwargs):
        mlog.debug(msg["start"])
        is_success = False
        for i in range(max_retry + 1):
            try:
                resp = rest(*args, **kwargs)
                resp.raise_for_status()
            except requests.exceptions.ConnectionError as e:
                mlog.error(e)
                mlog.error(f"网络连接错误，第{i}次")
            except requests.exceptions.HTTPError as e:
                mlog.error(e)
                mlog.error(f"HTTP错误，第{i}次")
            else:
                mlog.debug(msg["success"])
                is_success = True
            finally:
                if is_success:
                    break
                if i < _MAX_RETRY:
                    mlog.error(f"等待重试第{i + 1}次")
                    time.sleep(3)
                else:
                    mlog.critical(msg["fail"])
                    exitProc()
        return resp
    return wrapper


def sessionInit(CAS=False) -> requests.Session:
    """
        初始化一个requests.Session对象，清除初始header并设置UA

        返回值：
        session：   requests.Session对象
    """
    global config, url, log
    session = requests.Session()
    session.headers.clear()
    with open(os.path.join(os.path.dirname(__file__), "../config/common.json"), "r") as file:
        session.headers['User-Agent'] = json.load(file)["User-Agent"]
    if not CAS:
        return session

    log.debug("请求登入CAS")
    is_success = False
    for i in range(_MAX_RETRY + 1):
        try:
            resp = session.get(url=url["cas"])
            resp.raise_for_status()
            varid = BeautifulSoup(
                resp.text, "html.parser"
            ).find(attrs={"name": "execution"})["value"]
            post_data = {
                "username": config["cas"]["username"],
                "password": config["cas"]["password"],
                "type": "username_password",
                "submit": "LOGIN",
                "_eventId": "submit",
                "execution": varid
            }
            resp = session.post(url=url["cas"], data=post_data)
            resp.raise_for_status()
        except requests.exceptions.ConnectionError as e:
            log.error(e)
            log.error(f"网络连接错误，第{i}次")
        except requests.exceptions.HTTPError as e:
            log.error(e)
            log.error(f"HTTP错误，第{i}次")
        else:
            log.debug("成功登入CAS")
            is_success = True
        finally:
            if is_success:
                return session
            if i < _MAX_RETRY:
                log.error(f"等待重试第{i + 1}次")
                time.sleep(3)
            else:
                log.error("达到最大重试次数，登录失败")
    return None


def html_table_to_png(html):
    im = Image.open(os.path.join(os.path.dirname(__file__), "../holder.png"))
    print(im.format, im.size, im.mode)


# html_table_to_png("")
