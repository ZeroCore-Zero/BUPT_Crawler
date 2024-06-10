# import requests
import random
import base64
import json
import time
# import re

from function import bupt, jwgl  # 函数库

# 读取数据
config, urls = bupt.loadData()
# 构造Session
session = bupt.sessionInit()

# 登录
b64Acc = base64.b64encode(config["username"].encode()).decode()
b64Pwd = base64.b64encode(config["password"].encode()).decode()
post_data = {"encoded": b64Acc + r"%%%" + b64Pwd}
session.post(url=urls["jwgl"]["login"], data=post_data)

# 获取选课界面网址
# link=re.findall(r'\/jsxsd\/xsxk\/xklc_view\?jx0502zbid=.*"',resp.content.decode(),re.MULTILINE)
# link=link[0]
# link=link[:-1]
# link="https://jwgl.bupt.edu.cn"+link
# resp=session.get(link)
session.get(
    url="https://jwgl.bupt.edu.cn/jsxsd/xsxk/xsxk_index?jx0502zbid=FE81621AE8DC45C18202DB2101EFB209")
session.get(url="https://jwgl.bupt.edu.cn/jsxsd/xsxkkc/comeInGgxxkxk")
data = {
    "kcid": "85F6EA8ADC854FA3AF83A8F75197576B",
    "cfbs": "null",
    "jx0404id": "202320242006833",
    "xkzy": "",
    "trjf": "",
    "_": int(time.time() * 1000)
}

counter = 1
flag = True
while (flag):
    resp = session.post(
        url="https://jwgl.bupt.edu.cn/jsxsd/xsxkkc/xxxkOper", data=data)
    result = json.loads(resp.text)

    if (result["message"] == "选课成功"):
        print("{}\t选上啦\\^o^/,现在是{}".format(result["message"], time.ctime()))
        flag = False
    else:
        print("{}\t第{}次选课，没选上QAQ，现在是{}".format(
            result["message"], counter, time.ctime()))
        counter += 1
        sleeptime = random.random() + random.random() * 10
        print("休眠{}s".format(sleeptime))
        time.sleep(random.random() + 1)
