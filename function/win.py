from bs4 import BeautifulSoup
from . import bupt
from urllib.parse import urljoin
import json
import time
import os

name = "大学生创新创业训练计划平台"
baseURL = "http://win.bupt.edu.cn/"
session = bupt.sessionInit()
with open(os.path.join(os.path.dirname(__file__), "../config/bupt.json"), "r") as file:
    config = json.load(file)["win"]
with open(os.path.join(os.path.dirname(__file__), "../url/bupt.json"), "r") as file:
    url = json.load(file)["win"]
# 似乎不需要登录也能获取通知列表
# session.post(url=url["login"], data={
#     "user": config["username"],
#     "pass": config["password"]
# })


def get_notice_list():
    global session, url
    noticesHTML = BeautifulSoup(
        session.get(url["notice"]).text, "html.parser"
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
            "img": bupt.html_table_to_png(para)
        }]
    for node in para.contents:
        payload += handle_node(node)
    return payload


def get_content(url):
    global session
    page = {}
    contentHTML = BeautifulSoup(
        session.get(url).text, "lxml"
    )
    page["title"] = contentHTML.h2.text
    page["content"] = []
    page["attachment"] = []

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
    global session
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
    page = get_content(item["url"])
    content = {
        "title": page["title"],
        "content": page["content"]
    }
    if page["attachment"]:
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
