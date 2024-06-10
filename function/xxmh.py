from bs4 import BeautifulSoup
import requests
from . import bupt, logger
from urllib.parse import urljoin
import json
import time
import os
import sys


_MAX_RETRY = 5
name = "信息服务门户"
baseURL = "http://my.bupt.edu.cn/"
log = logger.getLogger(__name__)
session = None
with open(os.path.join(os.path.dirname(__file__), "../url/bupt.json"), "r") as file:
    url = json.load(file)["xxmh"]


# 登录函数
def login():
    global session, log
    log.debug("获取Session")
    session = bupt.sessionInit(CAS=True)
    if not session:
        log.critical("获取Session失败")
        bupt.exitProc()
    log.debug(f"登录到{name}")
    is_success = False
    for i in range(_MAX_RETRY + 1):
        try:
            resp = session.get(url=url["index"])
            resp.raise_for_status()
        except requests.exceptions.ConnectionError as e:
            log.error(e)
            log.error(f"网络连接错误，第{i}次")
        except requests.exceptions.HTTPError as e:
            log.error(e)
            log.error(f"HTTP错误，第{i}次")
        else:
            log.debug("登录成功")
            is_success = True
        finally:
            if is_success:
                return
            if i < _MAX_RETRY:
                log.error(f"等待重试第{i + 1}次")
                time.sleep(3)
            else:
                log.critical("达到最大重试次数，登录失败")
                bupt.exitProc()


login()


def getImgBinary(url):
    global session, log
    msg = {
        "start": "获取图片文件",
        "success": "获取成功",
        "fail": "达到最大重试次数，获取失败"
    }
    resp = bupt.autoRetryRequest(msg, log)(session.get, url)
    return resp.content


# 格式化通知列表
def get_notice_list():
    global session, url, log
    msg = {
        "start": "获取通知列表",
        "success": "获取成功",
        "fail": "达到最大重试次数，获取失败"
    }
    resp = bupt.autoRetryRequest(msg, log)(session.get, url["notice"])
    log.debug("解析查询结果")
    noticesHTML = BeautifulSoup(
        resp.text, "lxml"
    ).find(attrs={"class": "newslist list-unstyled"})
    noticeList = [
        {
            "title": item.a["title"],
            "author": item.find("span", attrs={"class": "author"}).text,
            "time": item.find("span", attrs={"class": "time"}).text,
            "url": "http://my.bupt.edu.cn/" + item.a["href"]
        }
        for item in noticesHTML.find_all("li")
    ]
    noticeList.reverse()
    return noticeList


def get_content(url):
    global session, log
    page = {}
    msg = {
        "start": "获取内容详情",
        "success": "获取成功",
        "fail": "达到最大重试次数，获取失败"
    }
    resp = bupt.autoRetryRequest(msg, log)(session.get, url)
    log.debug("解析查询结果")
    contentHTML = BeautifulSoup(
        resp.text, "lxml"
    )
    page["title"] = contentHTML.h1.text
    page["content"] = []
    for para in contentHTML.find(attrs={"class": "v_news_content"}).find_all("p"):
        content = None
        if para.span is not None:
            content = {
                "tag": "text",
                "text": para.text.strip()
            } if para.text.strip() else None
        if para.img is not None:
            imgURL = urljoin(baseURL, para.img["src"])
            log.debug(f"发现图片{imgURL}")
            content = {
                "tag": "img",
                "img": getImgBinary(imgURL)
            }
        if content is not None:
            page["content"].append([content])
    page["attachment"] = [
        {
            "file": batch.a.text,
            "link": baseURL + batch.a["href"]
        } for batch in contentHTML.find(attrs={"class": "battch"}).ul.find_all("li")
    ] if contentHTML.find(attrs={"class": "battch"}).ul is not None else []
    return page


def send_feishu(item):
    global session, log
    log.debug(f"准备发往飞书的json结构，通知标题：{item['title']}，在{name}")
    log.debug("生成通知结构")
    notice = {
        "title": item["title"],
        "content": [
            [{
                "tag": "text",
                "text": f"{name}：{time.strftime('%Y-%m-%d %H:%M')}"
            }],
            [{
                "tag": "text",
                "text": f"发布部门：{item['author']}"
            }],
            [{
                "tag": "text",
                "text": f"发布时间：{item['time']}"
            }],
            [
                {
                    "tag": "a",
                    "text": "原文地址",
                    "href": urljoin(baseURL, item["url"])
                },
                {
                    "tag": "at",
                    "user_id": "all",
                    "user_name": "所有人"
                }
            ]
        ]
    }
    log.debug("获取详情页面结构")
    page = get_content(item["url"])
    log.debug("生成内容结构")
    content = {
        "title": page["title"],
        "content": page["content"]
    }
    if page["attachment"]:
        log.debug("存在附件，添加附件结构")
        content["content"] += [[{
            "tag": "hr"
        }]] + [[{
            "tag": "text",
            "text": "附件如下：",
            "style": ["bold"]
        }]] + [
            [{
                "tag": "a",
                "text": batch["file"],
                "href": urljoin(baseURL, batch["link"])
            }] for batch in page["attachment"]
        ]
    return notice, content
