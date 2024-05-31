from bs4 import BeautifulSoup
from requests_toolbelt import MultipartEncoder
import requests
import io


# 登录CAS
def login_CAS(session, casUrl, username, password):
    varid = BeautifulSoup(
        session.get(url=casUrl).text, "html.parser"
    ).find(attrs={"name": "execution"})["value"]
    post_data = {
        "username": username,
        "password": password,
        "type": "username_password",
        "submit": "LOGIN",
        "_eventId": "submit",
        "execution": varid
    }
    session.post(url=casUrl, data=post_data)


# 格式化通知列表
def format_Notices(noticesHTML):
    noticeList = [
        {
            "title": item.a["title"],
            "author": item.find("span", attrs={"class": "author"}).text,
            "time": item.find("span", attrs={"class": "time"}).text,
            "url": "http://my.bupt.edu.cn/" + item.a["href"]
        }
        for item in noticesHTML.find_all("li")
    ]
    return noticeList


# 获取飞书图片标识
def getImageKey(imgurl, url, config):
    img = requests.get(imgurl).content
    token = requests.post(
        url=url["tenant_access_token"],
        headers={
            "Content-Type": "application/json; charset=utf-8"
        },
        json={
            "app_id": config["appID"],
            "app_secret": config["appSecret"]
        }
    ).json()["tenant_access_token"]     # 没做错误处理
    data = MultipartEncoder({
        "image_type": "message",
        "image": (io.BytesIO(img))
    })
    rp = requests.post(
        url=url["imgUpload"],
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": data.content_type
        },
        data=data
    )
    return rp.json()["data"]["image_key"]       # 也没做


# 发送飞书消息-通知
def send_notice(item, webhook):
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
    return requests.post(
        url=webhook,
        headers={"Content-Type": "application/json"},
        json={
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": content
                }
            }
        }
    ).json()["msg"]


# 发送飞书消息-内容
def send_content(page, webhook, feishuURL, feishuConfig):
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
                    "image_key": getImageKey(text, feishuURL, feishuConfig)
                }] for text in content
            ]
    }

    if attachment:
        main["content"] = main["content"] + [{
            "tag": "text",
            "text": ""
        }] + [{
            "tag": "text",
            "text": "**附件如下：**"
        }] + [
            [{
                "tag": "a",
                "text": batch["file"],
                "href": batch["link"]
            }] for batch in attachment
        ]

    return requests.post(
        url=webhook,
        headers={"Content-Type": "application/json"},
        json={
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": main
                }
            }
        }
    ).json()["msg"]
