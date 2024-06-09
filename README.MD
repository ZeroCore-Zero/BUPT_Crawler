# BUPT Crawer

BUPT Crawer 是一个为方便北邮学生获取数据而编写的爬虫程序

**请在遵循[《北京邮电大学校园网电子资源使用及管理办法（暂行）》](https://lib.bupt.edu.cn/a/ziyuan/dianziziyuan/guanlibanfa/)，[《电子资源使用说明》](https://lib.bupt.edu.cn/a/ziyuan/dianziziyuan/banquanshuoming/)等的前提下使用**

## 使用指南

### 爬取通知

> [!NOTE]
> 没有制作错误处理，所以请小心使用或者浏览源码后使用

定时获取信息门户消息，通过飞书自建应用/自定义机器人webhook（制作中）推送。

1. 准备工作
   - 登录[飞书开放平台-开发者后台](https://open.feishu.cn/app)，创建企业自建应用，添加`机器人`应用能力，并开通`im:chat`（获取与更新群组信息），`im:message`（获取与发送单聊、群组消息），`im:resource`（获取与上传图片或文件资源）权限。
   - 在`config`文件夹中，`bupt.json.example`填入校园网账号和密码，`feishu.json.example`中填入飞书自建应用的`appid`和`appsecret`，并将两个文件名中的`*.json.example`改为`*.json`。
2. 运行程序
   - 控制台运行：
      ```shell
      # 直接运行
      python getInfo.py
      # 后台运行
      nohup python getInfo.py > BUPT_Crawler.log 2&>1 &
      ```
   - 使用docker运行
      ```shell
      docker build -t bupt_crawler .
      docker run -td bupt_crawler
      ```


> TODO：\
> 异常捕获及处理 \
> 丰富测试消息，完善测试和发布两个通道的功能
> 所有URL使用urllib.prase解析
> 函数：获取飞书文件标识，表格转图片

### 辅助抢课

> 开发中
