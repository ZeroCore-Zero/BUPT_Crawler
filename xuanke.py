import requests
import base64
import re

import bupt_funcs   #函数库

# 读取数据
config,urls=bupt_funcs.loadData()
# 构造Session
session=bupt_funcs.sessionInit()

# 登录
b64Acc=base64.b64encode(config["username"].encode()).decode()
b64Pwd=base64.b64encode(config["password"].encode()).decode()
post_data={"encoded":b64Acc+r"%%%"+b64Pwd}
resp=session.post(url=urls["jwgl"]["login"], data=post_data)


# # 获取选课界面网址
# link=re.findall(r'\/jsxsd\/xsxk\/xklc_view\?jx0502zbid=.*"',resp.content.decode(),re.MULTILINE)
# link=link[0]
# link=link[:-1]
# link="https://jwgl.bupt.edu.cn"+link
# resp=session.get(link)

# bupt_funcs.write_to_file("zcxk.htm",resp.text)