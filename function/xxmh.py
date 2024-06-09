from bs4 import BeautifulSoup
from . import bupt
import json
import time
import os

name = "信息服务门户"
baseURL = "http://my.bupt.edu.cn/"
session = bupt.sessionInit(CAS=True)
with open(os.path.join(os.path.dirname(__file__), "../url/bupt.json"), "r") as file:
    url = json.load(file)["xxmh"]
session.get(url=url["index"])    # 信息门户单独认证


# 格式化通知列表
def get_notice_list():
    global session, url
    noticesHTML = BeautifulSoup(
        session.get(url["notice"]).text, "html.parser"
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
    global session
    page = {}
    contentHTML = BeautifulSoup(
        session.get(url).text, "html.parser"
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
            content = {
                "tag": "img",
                "img": session.get(baseURL + para.img["src"]).content
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
