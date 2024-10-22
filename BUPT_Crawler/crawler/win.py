from bs4 import BeautifulSoup
from . import bupt, logger
from urllib.parse import urljoin
# # import requests
# import sys
import json
import time
import os

# _MAX_RETRY = 5
name = "大学生创新创业训练计划平台"
baseURL = "http://win.bupt.edu.cn/"
log = logger.getLogger(__name__)
session = None
with open(os.path.join(os.path.dirname(__file__), "../config/bupt.json"), "r") as file:
    config = json.load(file)["win"]
with open(os.path.join(os.path.dirname(__file__), "../url/bupt.json"), "r") as file:
    url = json.load(file)["win"]


# 登录函数
def login():
    global session, config, url, log
    log.debug("获取Session")
    session = bupt.sessionInit()
    if not session:
        log.critical("获取Session失败")
        bupt.exitProc("获取Session失败")
    # # 似乎不需要登录也能获取通知列表
    # log.debug(f"登录到{name}")
    # is_success = False
    # for i in range(_MAX_RETRY + 1):
    #     try:
    #         resp = session.post(url=url["login"], data={
    #             "user": config["username"],
    #             "pass": config["password"]
    #         })
    #         resp.raise_for_status()
    #     except requests.exceptions.ConnectionError as e:
    #         log.error(e)
    #         log.error(f"网络连接错误，第{i}次")
    #         if i >= _MAX_RETRY:
    #             log.critical("达到最大重试次数，登录失败")
    #             bupt.exitProc(e)
    #     except requests.exceptions.HTTPError as e:
    #         log.error(e)
    #         log.error(f"HTTP错误，第{i}次")
    #         if i >= _MAX_RETRY:
    #             log.critical("达到最大重试次数，登录失败")
    #             bupt.exitProc(e)
    #     else:
    #         log.debug("登录成功")
    #         is_success = True
    #     finally:
    #         if is_success:
    #             return
    #         if i < _MAX_RETRY:
    #             log.error(f"等待重试第{i + 1}次")
    #             time.sleep(3)


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
        resp.text, "html.parser"
    ).find(attrs={"class": "winlist"})
    noticeList = [
        {
            "title": item.a.text,
            "time": item.find_all("td")[1].text.split(" ")[0],
            "url": baseURL + item.a["href"]
        }
        for item in noticesHTML.table.tbody.find_all("tr")
    ]
    noticeList.reverse()
    return noticeList


def handle_node(para):
    global session
    payload = []
    if isinstance(para, str):
        return [{
            "tag": "text",
            "text": "".join(para.split())
        }] if "".join(para.split()) else []
    try:
        if "display:none" in para["style"]:
            return []
    except KeyError:
        pass
    if para.name == "img":
        return [{
            "tag": "img",
            "img": session.get(urljoin(baseURL, para["src"])).content
        }]
    if para.name == "a":
        return [{
            "tag": "a",
            "text": "".join(para.text.split()),
            "href": urljoin(baseURL, para["href"])
        }]
    if para.name == "br":
        return [{
            "tag": "br"
        }]
    if para.name == "table":
        return [{
            "tag": "img",
            "img": bupt.html_table_to_png(baseURL, para)
        }]
    for node in para.contents:
        payload += handle_node(node)
    return payload


def get_content(url):
    global session
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
    page["title"] = contentHTML.h2.text
    page["content"] = []
    page["attachment"] = [] # 本来是想分开的，但是大创网站的内容和附件融为一体，所以这项被弃用了，懒得删
    # 大创网站的页面html结构十分费解，所以下面的解析结构也十分费解（咱要文明~）
    for para in contentHTML.find(attrs={"class": "entry-content notopmargin"}).children:
        if isinstance(para, str):
            continue
        line_info = handle_node(para)
        if line_info and not all(node["tag"] == "br" for node in line_info):
            page["content"].append(line_info)
    tmp_list = []
    for item in page["content"]:
        need_split = False
        have_br = False
        have_nbr = False
        for tag in item:
            if tag["tag"] != "br":
                have_nbr = True
            else:
                have_br = True
        if have_br and have_nbr:
            need_split = True
        if not need_split:
            tmp_list.append(item)
        if need_split:
            last_index = 0
            for i, tag in enumerate(item):
                if tag["tag"] == "br":
                    if last_index != i:
                        tmp_list.append(item[last_index:i])
                    last_index = i + 1
            if last_index != len(item):
                tmp_list.append(item[last_index:])
    page["content"] = tmp_list
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
                "text": f"发布时间：{item['time']}"
            }],
            [
                {
                    "tag": "a",
                    "text": "原文地址",
                    "href": item["url"]
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
                "href": batch["link"]
            }] for batch in page["attachment"]
        ]
    return notice, content


login()
