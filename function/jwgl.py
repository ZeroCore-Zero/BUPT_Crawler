# 教务系统抢课专用函数

def jwEncode(salt:str,name:str,pswd:str) -> str:
    """
        北邮教务登录加密算法，改写JS得来，在https://jwgl.bupt.edu.cn
        （吐槽：/jsxsd的那个就是个base64···这算哪门子加密）

        参数：
        salt：      获取的盐
        name：      学号
        pswd：      密码

        返回值：
        encoded：   密文
    """
    scode,sxh=salt.split("#")
    code=name+r"%%%"+pswd
    encoded=""
    for i in range(0,len(code)+1):
        if i<20:
            encoded=encoded+code[i:i+1]+scode[0:int(sxh[i:i+1])]
            scode=scode[int(sxh[i:i+1]):len(scode)]
        else:
            encoded=encoded+code[i:len(code)]
            break
    return encoded