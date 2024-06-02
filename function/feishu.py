from requests_toolbelt import MultipartEncoder
from bs4 import BeautifulSoup
import requests
import json
import io
import os

with open(os.path.join(os.path.dirname(__file__), "../config/feishu.json")) as file:
    config = json.load(file)
with open(os.path.join(os.path.dirname(__file__), "../url/feishu.json")) as file:
    url = json.load(file)


# 获取tenant_access_token
def get_tenant_access_token():
    global url, config
    return requests.post(
        url=url["tenant_access_token"],
        headers={
            "Content-Type": "application/json; charset=utf-8"
        },
        json={
            "app_id": config["appID"],
            "app_secret": config["appSecret"]
        }
    ).json()["tenant_access_token"]


# 获取机器人群组id列表
def getGroupsID():
    global url, config
    header = {
        "Authorization": "Bearer " + get_tenant_access_token()
    }
    resp = requests.get(url=url["get_groupid"], headers=header).json()
    chatList = [{
        "name": item["name"],
        "chat_id": item["chat_id"]
    } for item in resp["data"]["items"]]
    while resp["data"]["has_more"]:
        resp = requests.get(url=url["get_groupid"], headers=header, params={
            "page_token": resp.json["data"]["page_token"]
        }).json()
        chatList += [{
            "name": item["name"],
            "chat_id": item["chat_id"]
        } for item in resp["data"]["items"]]
    return chatList


# 获取飞书图片标识
def getImageKey(imgurl):
    global url, config
    img = requests.get(imgurl).content
    data = MultipartEncoder({
        "image_type": "message",
        "image": (io.BytesIO(img))
    })
    rp = requests.post(
        url=url["imgUpload"],
        headers={
            "Authorization": "Bearer " + get_tenant_access_token(),
            "Content-Type": data.content_type
        },
        data=data
    )
    return rp.json()["data"]["image_key"]


# 生成通知json结构
def generate_notice_content(item):
    content = {
        "title": item["title"],
        "content": [
            [
                {
                    "tag": "text",
                    "text": f"发布部门：{item['author']}"
                }
            ],
            [
                {
                    "tag": "text",
                    "text": f"发布时间：{item['time']}"
                }
            ],
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
    return content


# 生成内容json结构
def generate_page_content(page):
    page = BeautifulSoup(page, "html.parser")
    title = page.h1.text
    content = [item for item in [
        para.text.strip()
        if para.span is not None
        else "http://my.bupt.edu.cn/" + para.img["src"]
        if para.img is not None
        else None
        for para in page.find(attrs={"class": "v_news_content"}).find_all("p")
    ] if item not in [None, ""]]
    attachment = [
        {
            "file": batch.a.text,
            "link": "http://my.bupt.edu.cn/" + batch.a["href"]
        } for batch in page.find(attrs={"class": "battch"}).ul.find_all("li")
    ] if page.find(attrs={"class": "battch"}).ul is not None else []

    main = {
        "title": title,
        "content":
            [
                [{
                    "tag": "text",
                    "text": text
                }] if "http://my.bupt.edu.cn/" not in text
                else [{
                    "tag": "img",
                    "image_key": getImageKey(text)
                }] for text in content
            ]
    }

    if attachment:
        main["content"] += [[{
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
            }] for batch in attachment
        ]

    return main


# 发送飞书消息-自建应用-通知
def send_to_group(item, page):
    global url
    header = {
        "Authorization": "Bearer " + get_tenant_access_token(),
        "Content-Type": "application/json; charset=utf-8"
    }
    groups = getGroupsID()
    rpmsg = []
    for group in groups:
        notice_resp = requests.post(
            url=url["send_message"],
            params={"receive_id_type": "chat_id"},
            headers=header,
            json={
                "receive_id": group["chat_id"],
                "msg_type": "post",
                "content": json.dumps({
                    "zh_cn": generate_notice_content(item)
                })
            }
        )
        content_resp = requests.post(
            url=url["send_message"],
            params={"receive_id_type": "chat_id"},
            headers=header,
            json={
                "receive_id": group["chat_id"],
                "msg_type": "post",
                "content": json.dumps({
                    "zh_cn": generate_page_content(page)
                })
            }
        )
        rpmsg.append({
            "name": group["name"],
            "message": {
                "notice": notice_resp.json()["msg"],
                "content": content_resp.json()["msg"]
            }
        })
    return rpmsg
