from bs4 import BeautifulSoup
from . import common

session = common.sessionInit()


# 登录CAS
def login(casUrl, tzUrl, username, password):
    global session
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
    session.get(url=tzUrl)    # 信息门户单独认证


# 格式化通知列表
def get_notice_list(url):
    global session
    noticesHTML = BeautifulSoup(
        session.get(url).text, "html.parser"
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
    return noticeList


def get_content(url):
    global session
    page = {}
    contentHTML = BeautifulSoup(
        session.get(url).text, "html.parser"
    )
    page["title"] = contentHTML.h1.text
    page["content"] = [item for item in [
        para.text.strip()
        if para.span is not None
        else "http://my.bupt.edu.cn/" + para.img["src"]
        if para.img is not None
        else None
        for para in contentHTML.find(attrs={"class": "v_news_content"}).find_all("p")
    ] if item not in [None, ""]]
    page["attachment"] = [
        {
            "file": batch.a.text,
            "link": "http://my.bupt.edu.cn/" + batch.a["href"]
        } for batch in contentHTML.find(attrs={"class": "battch"}).ul.find_all("li")
    ] if contentHTML.find(attrs={"class": "battch"}).ul is not None else []
    return page
