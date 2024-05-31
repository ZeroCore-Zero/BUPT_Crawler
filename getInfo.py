from function import common, xxmh  # 函数库
from bs4 import BeautifulSoup
from time import sleep
import pickle
import os

_ARCHIVED_NOTICES = True
_PUBLISHED = True

if __name__ == "__main__":
    # 准备工作
    os.chdir(os.path.dirname(__file__))
    config, urls = common.loadData()        # 读取数据
    session = common.sessionInit()          # 构造Session
    xxmh.login_CAS(session, urls["cas"], config["username"], config["password"])
    session.get(urls["xxmh"]["tongzhi"])    # 信息门户单独认证
    notice_storages = []
    if _ARCHIVED_NOTICES:
        with open("notice.pickle", "rb") as archive_file:
            notice_storages = pickle.load(archive_file)

    # 爬取信息
    while True:
        notices = xxmh.format_Notices(
            BeautifulSoup(session.get(urls["xxmh"]["tongzhi"]).text, "html.parser")
            .find(attrs={"class": "newslist list-unstyled"})
        )

        for item in notices:
            if any(item["title"] == archive["title"] for archive in notice_storages):
                continue
            # 如果是新消息就存档并发送
            notice_storages.append(item)
            if len(notice_storages) > 100:
                notice_storages.pop(0)
            with open("notice.pickle", "wb") as archive_file:
                pickle.dump(notice_storages, archive_file)

            print(item["title"])
            for webhook in config["webhook"]:
                if webhook["statues"] == "release" and not _PUBLISHED:
                    print(f'webhook {config["webhook"].index(webhook)}, not publish')
                    continue
                notice_msg = xxmh.send_notice(item, webhook["url"])
                content_msg = xxmh.send_content(
                    session.get(item["url"]).text,
                    webhook["url"], urls["feishu"], config["feishu"])
                print(f'webhook {config["webhook"].index(webhook)}, {notice_msg=}, {content_msg=}')
        sleep(60)
