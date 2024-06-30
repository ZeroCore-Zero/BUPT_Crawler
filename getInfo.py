from crawler import feishu, xxmh, win, logger, bupt  # 函数库
import time
import os


_MAX_STORAGE = 100
_MAX_EMPTY_HIT = 10
log = logger.getLogger(os.path.basename(__file__).split(".")[0])


def main():
    # 准备工作
    BaseSites = [
        xxmh,
        win
    ]
    log.debug(f"共加载{len(BaseSites)}个模块，分别为:")
    for site in BaseSites:
        log.debug(site.name)
    sites = {site.name: site for site in BaseSites}
    notice_storages = {sites[site].name: sites[site].get_notice_list() for site in sites}
    term_count = 0
    day_count = 0
    total_count = 0
    log.info("系统加载完毕")
    feishu.send_to_admin(f"{time.strftime('%Y-%m-%d %H:%M:%S')} 系统加载完毕")

    # 爬取信息
    while True:
        log.debug("定时查询任务")
        notices = {sites[site].name: sites[site].get_notice_list() for site in sites}

        for site in notices:
            has_new = False
            for item in notices[site]:
                if any(item["title"] == archive["title"] for archive in notice_storages[site]):
                    continue
                # 如果是新消息就存档并发送
                log.info(f"发现新通知，在{sites[site].name}")
                has_new = True
                term_count = 0
                day_count += 1
                total_count += 1
                notice_storages[site].append(item)
                if len(notice_storages[site]) > _MAX_STORAGE:
                    log.debug("缓存通知已达上限，即将释放部分通知")
                    for _ in range(_MAX_STORAGE // 10):
                        log.debug(f"释放通知，标题{notice_storages[site][0]['title']}，时间{notice_storages[site][0]['time']}")
                        notice_storages[site].pop(0)
                log.info("消息推送到飞书")
                messages = feishu.send_to_group(
                    *sites[site].send_feishu(item)
                )
                for msg in messages:
                    log.info(f"{sites[site].name}: {msg['name']}: 通知 {msg['message']['notice']}, 内容 {msg['message']['content']}")
            if not has_new:
                term_count += 1
                log.debug(f"{sites[site].name}: 没有新通知")

        if term_count == len(sites) * _MAX_EMPTY_HIT:
            log.info(f"连续{_MAX_EMPTY_HIT}分钟没有新消息")
            term_count = 0

        # 每天晚上十点向管理员发送每日总结
        if time.strftime('%H') == "22":
            feishu.send_to_admin(f"{time.strftime('%Y-%m-%d')} 本日共发送消息{day_count}条，总计发送消息{total_count}")
            day_count = 0

        time.sleep(60)


if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        print(e)
        log.critical("程序由于异常退出")
        bupt.exitProc(e)
