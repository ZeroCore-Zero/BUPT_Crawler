from bs4 import BeautifulSoup
from time import sleep
# import logging
# import requests
# import json
# import re

import bupt_funcs   #函数库

# 读取数据
config,urls=bupt_funcs.loadData()
# 构造Session
session=bupt_funcs.sessionInit()

# 登录CAS
resp=session.get(url=urls["cas"])
soup=BeautifulSoup(resp.text,"html.parser")
varid=soup.find(attrs={"name":"execution"})["value"]
post_data={
    "username":config["username"],
    "password":config["password"],
    "type":"username_password",
    "submit":"LOGIN",
    "_eventId":"submit",
    "execution":varid
}
session.post(url=urls["cas"],data=post_data)

# 爬取信息门户
session.get(urls["xxmh"]["login"])  # 信息门户有单独认证，需要单独发一个get拿到认证
for i in range(2181,10000):
    filename="xxmh_{}.htm".format(i)
    print("Getting site {} ...".format(filename))
    bupt_funcs.write_to_file("./xxmh/{}".format(filename),
                             session.get("http://my.bupt.edu.cn/list.jsp?urltype=tree.TreeTempUrl&wbtreeid={}".format(i)).text)
    print("Site {} is writen,please wait...".format(filename))
    sleep(0.1)




# resp=session.get(urls["xxmh"]["tongzhi"])
# bupt_funcs.write_to_file("temp.htm",resp.text)