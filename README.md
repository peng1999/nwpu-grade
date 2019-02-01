**本项目复刻自 <https://github.com/Dy1aNT/NWPUgrade.git>**

# NWPUgrade
NWPU成绩通知机

## 简介
秉承着技术改变生活的态度写了这个脚本，利用它你可以做到：

* 再也无需不厌其烦地登陆教务系统查看成绩

* 每次新成绩出炉都会有邮件发送至你邮箱

* 让你永远领先别人一步得到最新成绩

* 并且自动计算目前为止所有课程成绩的学分绩发送至邮箱

## 环境
Python 3

## 具体步骤

1. 你只需找一台云服务器(测试用的阿里云Ubuntu)

2. 将 config.py 中的 username 和 password 换成你的学号和密码
```python
username = "xxxxxxxxxx"  # username:学号
password = "xxxxxxxxxx"  # password:密码
```
3. 将 config.py 中的发送邮箱、邮箱密码、接收邮箱以及 smtp 服务器地址修改成你的
```python
from_addr = 'xxx@163.com'  # 发送邮件的邮箱
password = '你的邮箱密码'  # 发送邮箱的密码
to_addr = '123456@qq.com'  # 用于接收邮件的邮箱
smtp_server = 'smtp.163.com'  # smtp服务器
```
4. 输入命令后台执行代码

```sh
$ nohup python NWPUgrade.py &
```

值得一提的是，测试时用的是阿里云服务器，而阿里云服的25端口都是默认禁止的，所以脚本中的邮件端口改为456。如果你使用的环境没有这种限制，可以改回25端口。

## 其他版本

**input.py**

如果没有找到 config.py 将会从命令行读取用户名和密码。

```sh
python input.py
```
