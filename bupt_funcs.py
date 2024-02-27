from bs4 import BeautifulSoup
import requests
import inspect
import json
import os

########################################
# 通用函数

def write_to_file(filename:str,text:str):
    """
        把内容写入文件，用于导出response.text

        参数：
        filename:   要写入的文件
        text:       要写入的内容
    """
    with open(filename,'w') as file:
        file.write(text)

def sessionInit() -> requests.Session:
    """
        初始化一个requests.Session对象，清除初始header并设置UA

        返回值：
        session：   requests.Session对象
    """
    session=requests.Session()
    session.headers.clear()
    #session.headers['User-Agent']=para["ua"]
    return session

def loadData() -> tuple[dict,dict]:
    """
        载入数据，将json配置信息转换为内置字典格式

        返回值：
        config:     个人信息
        urls:       北邮网址

    """
    with open("config.json","r") as config, open("urls.json","r") as urls:
        return json.load(config),json.load(urls)
    
def getCurrentFile() -> str:
    """
        返回当前文件的文件地址

        返回值：
        current_file：文件地址
    """
    current_file = inspect.getframeinfo(inspect.currentframe().f_back).filename
    return current_file

def getCallerFile() -> str:
    """
        返回调用函数的文件地址

        返回值：
        caller_file：文件地址
    """
    caller_file=inspect.stack()[2].filename
    return caller_file
########################################
# 信息门户爬虫专用函数
    
def delUnusableHTML(dirpath:str):
    """
        删除按照序列号爬取的信息门户html文件中的无效页面

        参数：
        dirpath:    html文件所在目录
    """
    fileNumber=len(os.listdir(dirpath))
    for filename in fileNumber:
        filepath="{}/{}".format(dirpath,filename)
        isUsable=True
        try:
            with open(filepath, "r") as file:
                soup=BeautifulSoup(file,"html.parser")
                if(soup.span.string=="栏目不存在!"):
                    print("file {} is unusable!".format(filename))
                    isUsable=False
        except FileNotFoundError:
            print("file {} can't be found!".format(filename))
            continue
        if not isUsable:
            os.remove(filepath)

def getPages(dirpath):
    """
        获取审计页面列表

        参数：
        dirpath：   页面列表所在目录
        返回值：
        rpdata：    页面列表路径集合
    """
    filelist=os.listdir(os.path.dirname(getCallerFile())+"/"+dirpath)
    rpdata={}
    i=0
    for file in filelist:
        rpdata[i]=file
        # print(i,"\t:",file)
        i+=1
    rpdata=json.dumps(rpdata)
    return rpdata

def delPages(filepath):
    """
        审计页面时假删除

        参数：
        filepath：  文件路径

        返回值：
        rpdata：    操作状态（目前没啥用）
    """

    os.rename("")
    rpdata="perfect"
    return rpdata

def rmnPages(filepath):
    """
        审计页面时保留

        参数：
        filepath：  文件路径

        返回值：
        rpdata：    操作状态（目前没啥用）
    """

########################################
# 教务系统抢课专用函数

def jwEncode(salt:str,name:str,pswd:str):
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