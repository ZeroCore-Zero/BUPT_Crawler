# BUPT Crawer

BUPT Crawer 是一个为方便北邮学生获取数据而编写的爬虫程序

**请在使用时遵循以下规定**
- [《北京邮电大学校园网电子资源使用及管理办法（暂行）》](https://lib.bupt.edu.cn/a/ziyuan/dianziziyuan/guanlibanfa/)
- [《电子资源使用说明》](https://lib.bupt.edu.cn/a/ziyuan/dianziziyuan/banquanshuoming/)
- 相关法律法规

## 项目介绍

自动爬取设定平台上的新通知新消息，并转发到已配置的推送平台上。

支持的平台列表：
- [信息服务门户-校内通知](http://my.bupt.edu.cn/list.jsp?urltype=tree.TreeTempUrl&wbtreeid=1154)
- [大学生创新创业计划训练平台-公告中心](https://win.bupt.edu.cn/note.do)
- ~~[北京邮电大学邮箱](https://mail.bupt.edu.cn/)~~ 制作中
- ~~[云邮教学空间-消息通知](https://ucloud.bupt.edu.cn/uclass/index.html#/set/notice_fullpage)~~ 制作中
- ~~[云邮教学空间-所有课程的公告](https://ucloud.bupt.edu.cn/uclass/index.html#/student/myCourse)~~ 制作中

支持的推送方式列表：
- [飞书-机器人](https://open.feishu.cn/document/client-docs/bot-v3/bot-overview)

## 使用指南

1. 准备工作
   1. 个人配置
      - 在`config/bupt.json.example`中填入校园网账号和密码，并重命名文件为`config/bupt.json`。
   2. 飞书-应用机器人（**推荐**）
      - 在`config/feishu.json.example`中填入以下内容，并重命名文件为`config/feishu.json`：
        - 飞书自建应用的`appid`和`appsecret`
        - 管理员的账号信息，`mobile`填入手机号码，`email`填入邮箱地址，`open_id`填入Open ID，三选一即可
            > 无论填入何子项，为保护隐私，该父项随后均会被管理员的Open ID覆盖
            > **请只填入一项，其余两项填写null**
      - 注意应用应开启以下权限：
        - `im:chat`（获取与更新群组信息）
        - `im:message`（获取与发送单聊、群组消息）
        - `im:resource`（获取与上传图片或文件资源）
        - `contact:user.id:readonly`（通过手机号或邮箱获取用户 ID）
   3. 飞书-自定义机器人
      - 开发中... 
   
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
> 处理飞书返回HTTP错误码（飞书专用错误处理） 
