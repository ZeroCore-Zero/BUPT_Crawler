from bs4 import BeautifulSoup


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
def get_notice_list(session, url):
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
