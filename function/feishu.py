from requests_toolbelt import MultipartEncoder
import requests
import json
import io
import os

_DEBUG = True
with open(os.path.join(os.path.dirname(__file__), "../config/feishu.json")) as file:
    config = json.load(file)
with open(os.path.join(os.path.dirname(__file__), "../url/feishu.json")) as file:
    url = json.load(file)
if _DEBUG:
    config = {
        "appID": "cli_a6eae3ee74bb900c",
        "appSecret": "1r76MftBn6jQaW83QLYGlWJgRC8B55Pw"
    }


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
def getImageKey(img):
    global url, config
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


# 获取飞书文件标识
def getFileKey(file):
    pass


# 处理图片和文件的接口
def load_item(item):
    if item["tag"] == "img":
        item["image_key"] = getImageKey(item["img"])
        del item["img"]
    if item["tag"] == "file":
        item["file_key"] = getFileKey(item["file"])
        del item["file"]
    return item


# 处理传入的json为标准的飞书消息api格式
def handle_content(content):
    payload = {
        "title": content["title"],
        "content": [[
            load_item(item)
            for item in para
        ] for para in content["content"]]
    }
    return payload


# 发送飞书消息-自建应用-通知
def send_to_group(item, content):
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
                    "zh_cn": handle_content(item)
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
                    "zh_cn": handle_content(content)
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
