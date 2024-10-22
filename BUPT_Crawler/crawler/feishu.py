from requests_toolbelt import MultipartEncoder
import requests
from . import bupt, logger
import json
import time
import sys
import io
import os


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
        json={
            "app_id": config["appID"],
            "app_secret": config["appSecret"]
        }
    )
    return resp.json()["tenant_access_token"]


def getOpenID(key, value):
    global url, log
    header = {
        "Authorization": "Bearer " + get_tenant_access_token()
    }
    data = {
        f"{key}s": [value]
    }
    resp = requests.post(url=url["get_openid"], headers=header, json=data)
    return resp.json()["data"]["user_list"][0]["user_id"]


# 获取机器人群组id列表
def getGroupsID():
    global url, config, log
    header = {
        "Authorization": "Bearer " + get_tenant_access_token()
    }
    resp = bupt.autoRetryRequest(
        {
            "start": "获取机器人群组id列表",
            "success": "获取成功",
            "fail": "达到最大重试次数，获取失败"
        }, log)(requests.get, url=url["get_groupid"], headers=header)
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


# 处理图片的接口
def load_item(item):
    global log
    if item["tag"] == "img":
        log.debug("图片项，调用图片接口")
        item["image_key"] = getImageKey(item["img"])
        del item["img"]
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
        "Authorization": "Bearer " + get_tenant_access_token()
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


def send_to_admin(message):
    global config, url, log
    if not isinstance(config["admin"], str):
        log.error("管理员配置尚未完成")
        return
    log.debug(f"向管理员发送消息: {message}")
    is_success = False
    for i in range(_MAX_RETRY + 1):
        try:
            resp = requests.post(
                url=url["send_message"],
                headers={"Authorization": "Bearer " + get_tenant_access_token()},
                params={"receive_id_type": "open_id"},
                json={
                    "receive_id": config["admin"],
                    "msg_type": "text",
                    "content": json.dumps({"text": f"{message}"})
                }
            )
            resp.raise_for_status()
        except requests.exceptions.ConnectionError as e:
            log.error(e)
            log.error(f"网络连接错误，第{i}次")
            if i >= _MAX_RETRY:
                log.critical("达到最大重试次数，发送失败")
                bupt.exitProc(e)
        except requests.exceptions.HTTPError as e:
            log.error(e)
            log.error(f"HTTP错误，第{i}次")
            if i >= _MAX_RETRY:
                log.critical("达到最大重试次数，发送失败")
                bupt.exitProc(e)
        else:
            log.debug("发送成功")
            is_success = True
        finally:
            if is_success:
                break
            if i < _MAX_RETRY:
                log.error(f"等待重试第{i + 1}次")
                time.sleep(3)


_MAX_RETRY = 5
log = logger.getLogger(__name__)
with open(os.path.join(os.path.dirname(__file__), "../url/feishu.json")) as file:
    url = json.load(file)
with open(os.path.join(os.path.dirname(__file__), "../config/feishu.json")) as file:
    config = json.load(file)

if isinstance(config["admin"], str):
    log.debug("管理员OpenID已获取")
else:
    log.debug("获取管理员OpenID")
    key = None
    value = None
    for item in config["admin"]:
        if config["admin"][item] is not None:
            if key is not None:
                log.critical("飞书管理员配置文件填入多于一项")
                sys.exit()
            key = item
            value = config["admin"][item]
    if key != "open_id":
        log.debug(f"使用{key}查询OpenID")
        openid = getOpenID(key, value)
    else:
        log.debug("初始配置文件中已填入OpenID")
        openid = value
    config["admin"] = openid
    with open(os.path.join(os.path.dirname(__file__), "../config/feishu.json"), "w") as file:
        json.dump(config, file)
