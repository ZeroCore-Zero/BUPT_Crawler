from bs4 import BeautifulSoup
import requests
from PIL import Image
import json
import os


with open(os.path.join(os.path.dirname(__file__), "../config/bupt.json"), "r") as file:
    config = json.load(file)
with open(os.path.join(os.path.dirname(__file__), "../url/bupt.json"), "r") as file:
    url = json.load(file)


def sessionInit(CAS=False) -> requests.Session:
    """
        初始化一个requests.Session对象，清除初始header并设置UA

        返回值：
        session：   requests.Session对象
    """
    session = requests.Session()
    session.headers.clear()
    with open(os.path.join(os.path.dirname(__file__), "../config/common.json"), "r") as file:
        session.headers['User-Agent'] = json.load(file)["User-Agent"]
    if CAS:
        varid = BeautifulSoup(
            session.get(url=url["cas"]).text, "html.parser"
        ).find(attrs={"name": "execution"})["value"]
        post_data = {
            "username": config["cas"]["username"],
            "password": config["cas"]["password"],
            "type": "username_password",
            "submit": "LOGIN",
            "_eventId": "submit",
            "execution": varid
        }
        session.post(url=url["cas"], data=post_data)
    return session


def html_table_to_png(html):
    with open(os.path.join(os.path.dirname(__file__), "../holder.png"), "rb") as img:
        return img.read()
