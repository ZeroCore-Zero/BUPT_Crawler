from requests_toolbelt import MultipartEncoder
import requests
from . import bupt, logger
import json
import io
import os

_DEBUG = True
log = logger.getLogger(__name__)
with open(os.path.join(os.path.dirname(__file__), "../config/feishu.json")) as file:
    config = json.load(file)
with open(os.path.join(os.path.dirname(__file__), "../url/feishu.json")) as file:
    url = json.load(file)
if _DEBUG:
    log.debug("调试模式开启，使用测试通道")
    config = config["test"]


# 获取tenant_access_token
def get_tenant_access_token():
    global url, config, log
    msg = {
        "start": "获取tenant_access_token",
        "success": "获取成功",
        "fail": "达到最大重试次数，获取失败"
    }
    resp = bupt.autoRetryRequest(msg, log)(
        requests.post,
        url=url["tenant_access_token"],
        headers={
            "Content-Type": "application/json; charset=utf-8"
        },
        json={
            "app_id": config["appID"],
            "app_secret": config["appSecret"]
        }
    )
    return resp.json()["tenant_access_token"]


# 获取机器人群组id列表
def getGroupsID():
    global url, config, log
    header = {
        "Authorization": "Bearer " + get_tenant_access_token()
    }
    msg = {
        "start": "获取机器人群组id列表",
        "success": "获取成功",
        "fail": "达到最大重试次数，获取失败"
    }
    resp = bupt.autoRetryRequest(msg, log)(requests.get, url=url["get_groupid"], headers=header)
    resp = resp.json()
    log.debug("格式化群组列表")
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
    global url, config, log
    log.debug("编码图片")
    data = MultipartEncoder({
        "image_type": "message",
        "image": (io.BytesIO(img))
    })
    msg = {
        "start": "获取飞书图片标识",
        "success": "获取成功",
        "fail": "达到最大重试次数，获取失败"
    }
    rp = bupt.autoRetryRequest(msg, log)(
        requests.post,
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
    global log
    if item["tag"] == "img":
        log.debug("图片项，调用图片接口")
        item["image_key"] = getImageKey(item["img"])
        del item["img"]
    if item["tag"] == "file":
        log.debug("文件项，调用文件接口")
        item["file_key"] = getFileKey(item["file"])
        del item["file"]
    else:
        log.debug("普通项，不做处理")
    return item


# 处理传入的json为标准的飞书消息api格式
def handle_content(content):
    global log
    log.debug("处理传入的json为标准的飞书消息api格式")
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
    global url, log
    log.debug("发送飞书消息-自建应用-通知")
    log.debug("准备工作")
    header = {
        "Authorization": "Bearer " + get_tenant_access_token(),
        "Content-Type": "application/json; charset=utf-8"
    }
    groups = getGroupsID()
    rpmsg = []
    for group in groups:
        log.debug(f"向飞书群组{group['name']}发送消息")
        msg = {
            "start": "发送通知标题",
            "success": "发送成功",
            "fail": "达到最大重试次数，发送失败"
        }
        notice_resp = bupt.autoRetryRequest(msg, log)(
            requests.post,
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
        msg = {
            "start": "发送通知内容",
            "success": "发送成功",
            "fail": "达到最大重试次数，发送失败"
        }
        content_resp = bupt.autoRetryRequest(msg, log)(
            requests.post,
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
