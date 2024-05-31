# BUPT Crawer

BUPT Crawer 是一个为方便北邮学生获取数据而编写的爬虫程序

**请在遵循[《北京邮电大学校园网电子资源使用及管理办法（暂行）》](https://lib.bupt.edu.cn/a/ziyuan/dianziziyuan/guanlibanfa/)，[《电子资源使用说明》](https://lib.bupt.edu.cn/a/ziyuan/dianziziyuan/banquanshuoming/)等的前提下使用**

## 文件目录
|    文件    |    描述    |    状态    |
|---------------|---------------|---------------|
|  **function**  |  可能会用到的一些公用函数库  |  已完成  |
|  xuanke.py  |  帮助抢课的脚本  |  未完成，正在编写  |
|  getInfo.py  |  爬取信息门户通知  |  初步完成  |
|  config.json  |  配置信息  |
|  urls.json  |  网址目录  |

## 使用指南

0. 在`config.json.example`中填入自己的配置信息，并重命名为`config.json`。

### 爬取通知

0. 脚本会定时获取信息门户消息，若有更新则会通过飞书机器人推送。
   >[!NOTE]
   >没有制作错误处理，所以请小心使用或者浏览源码后使用
1. 运行`getInfo.py`。

> TODO：\
> 异常捕获及处理 \
> 丰富测试消息，完善测试和发布两个通道的功能

### 辅助抢课

1. 运行`xuanke.py`。