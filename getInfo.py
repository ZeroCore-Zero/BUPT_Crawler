from function import feishu, xxmh, win  # 函数库
import time
import os


_MAX_STORAGE = 100


def main():
    # 准备工作
    os.chdir(os.path.dirname(__file__))
    sites = [
        xxmh,
        win
    ]
    sites = {site.__name__: site for site in sites}
    notice_storages = {sites[site].__name__: sites[site].get_notice_list() for site in sites}

    # 爬取信息
    while True:
        notices = {sites[site].__name__: sites[site].get_notice_list() for site in sites}
        print(time.strftime("%Y-%m-%d %H:%M"))

        for i, site in enumerate(notices):
            print(f"{i+1:02}. {sites[site].name}")
            has_new = False
            for item in notices[site]:
                if any(item["title"] == archive["title"] for archive in notice_storages[site]):
                    continue
                # 如果是新消息就存档并发送
                has_new = True
                notice_storages[site].append(item)
                if len(notice_storages[site]) > _MAX_STORAGE:
                    notice_storages[site].pop(0)
                print("- ", item["title"])
                messages = feishu.send_to_group(
                    *sites[site].send_feishu(item)
                )
                for msg in messages:
                    print(f"  {msg['name']}: 通知 {msg['message']['notice']}, 内容 {msg['message']['content']}")
            if not has_new:
                print("  没有新通知")

        time.sleep(60)


if __name__ == "__main__":
    main()
