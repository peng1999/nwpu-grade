# NWPUgrade
NWPU成绩查询/通知机

## 简介

* 再也无需不厌其烦地登陆教务系统查看成绩

* 每次新成绩出炉都会有Telegram消息推送

* 自动计算目前为止所有课程成绩的学分绩

## 环境

本项目需要运行在 Python 3.6 及更高的版本上。

命令行客户端依赖：

- lxml
- cssselect

Telegram Bot依赖：

- 所有命令行客户端依赖
- python-telegram-bot
- pydantic


## 部署 Telegram Bot

1. 克隆项目

   ```
   git clone https://github.com/peng1999/nwpu-grade.git
   ```

2. 安装 [Poetry](poetry)

   ```
   python3 -m pip install --user poetry
   ```

3. 利用 Poetry 安装 Python 环境

   ```
   poetry install
   ```

4. 利用 [Bot Father](https://t.me/BotFather) 创建一个 Telegram Bot。

4. 创建并修改 `config.py`

   ```
   cp config.py.example config.py
   vim config.py
   ```

5. 运行

   ```
   poetry run python bot.py
   ```

> 注：
> 1. Telegram Bot 无法在中国大陆正常访问，你可能需要配置代理。
> 3. Poetry 的其他安装方式见[官网](poetry)。
> 2. 如果不想使用 Poetry，也可以直接使用 pip 安装依赖包

[poetry]: https://python-poetry.org/

## 直接命令行查询

安装依赖后直接运行：

```
python3 client.py
```

可以在 `config.py` 中设置用户名和密码，则无需每次在命令行输入。

## 致谢

本项目部分代码来自 @Dy1aNT 已经停止更新的项目 <https://github.com/Dy1aNT/NWPUgrade.git>
