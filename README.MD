# BUPT Crawer

BUPT Crawer 是一个为方便北邮学生获取数据而编写的爬虫程序

**请在遵循[《北京邮电大学校园网电子资源使用及管理办法（暂行）》](https://lib.bupt.edu.cn/a/ziyuan/dianziziyuan/guanlibanfa/)，[《电子资源使用说明》](https://lib.bupt.edu.cn/a/ziyuan/dianziziyuan/banquanshuoming/)等的前提下使用**

## 文件目录
|    文件    |    描述    |    状态    |
|---------------|---------------|---------------|
|  **bupt_funcs.py**  |  可能会用到的一些公用函数库  |  已完成  |
|  xuanke.py  |  帮助抢课的脚本  |  未完成，正在编写  |
|  getInfo.py  |  爬取信息门户通知  |  未完成，正在编写  |
|  config.json  |  个人信息  |
|  urls.json  |  北邮网址目录  |

## 使用指南

0.在`config.json.example`中填入学号与密码，并重命名为`config.json`。

### 爬取通知

1.运行`getInfo.py`。

### 辅助抢课

1.运行`xuanke.py`。