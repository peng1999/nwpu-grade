# NWPUgrade
NWPU成绩查询/通知机

## 简介

* 再也无需不厌其烦地登陆教务系统查看成绩

* 每次新成绩出炉都会有Telegram消息推送

* 自动计算目前为止所有课程成绩的学分绩

## 环境
Python 3.6 及以上

命令行依赖：
- lxml
- cssselect

Telegram Bot依赖：
- python-telegram-bot
- pydantic

依赖包建议使用[Poetry](https://python-poetry.org/)安装：

```
poetry install
```

运行脚本时使用 `poetry run python <filename>`

## 使用方法

client.py可以作为命令行程序直接运行：
```
python client.py
```

Telegram Bot 通过 `bot.py` 运行：
```
python bot.py
```

所有的配置在 `config.py` 中，详见 `config.py.example` 的注释。

## 致谢

本项目部分代码来自 @Dy1aNT 已经停止更新的项目 <https://github.com/Dy1aNT/NWPUgrade.git>
