from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
from html2image import Html2Image
from . import logger, feishu
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


def exitProc(exception):
    global log
    log.critical(f"系统由于异常退出, {exception}")
    feishu.send_to_admin(f"{time.strftime('%Y-%m-%d %H:%M:%S')} 系统由于异常退出, {exception}")
    sys.exit()


def autoRetryRequest(msg, mlog, max_retry=_MAX_RETRY):
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
                if i >= max_retry:
                    mlog.critical(msg["fail"])
                    exitProc(e)
            except requests.exceptions.HTTPError as e:
                mlog.error(e)
                mlog.error(f"HTTP错误，第{i}次")
                if i >= max_retry:
                    mlog.critical(msg["fail"])
                    exitProc(e)
            else:
                mlog.debug(msg["success"])
                is_success = True
            finally:
                if is_success:
                    break
                if i < max_retry:
                    mlog.error(f"等待重试第{i + 1}次")
                    time.sleep(3)
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


def html_table_to_png(baseurl, table):
    global log
    log.debug("从html生成图片")
    # table = BeautifulSoup(html, 'lxml').find('table')
    for item in table.find_all("img"):
        item["src"] = urljoin(baseurl, item["src"])

    log.debug("生成图片")
    photo = Html2Image().screenshot(html_str=str(table), css_str='body {background: white;}')[0]
    log.debug("生成成功，读取到内存并删除缓存")
    with open(photo, "rb") as img:
        png = img.read()
    os.remove(photo)
    return png
