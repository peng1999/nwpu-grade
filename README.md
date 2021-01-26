# NWPUgrade
大学成绩查询/通知 Telegram Bot（现支持西工大和北航）

## 简介

* 再也无需不厌其烦地登陆教务系统查看成绩
  - 按学期/学年计算学分绩
  - 查看分数构成（平时成绩，实验成绩，卷面成绩）

* 每次新成绩出炉都会有Telegram消息推送

## 环境

本项目需要运行在 Python 3.6 及更高的版本上。
同时需要系统环境具有 sqlite3。

Python 包依赖：

- requests
- lxml
- cssselect
- python-telegram-bot
- pydantic
- peewee


## 部署 Telegram Bot

### 普通方式

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
   poetry run python launch_bot.py
   ```

> 注：
> 1. Telegram 无法在中国大陆正常访问，你可能需要配置代理。
> 3. Poetry 的其他安装方式见[官网](poetry)。
> 2. Poetry 不是必须的，也可以直接使用 pip 安装依赖包

[poetry]: https://python-poetry.org/

### Docker 部署

1. 克隆项目

   ```
   git clone https://github.com/peng1999/nwpu-grade.git
   ```

2. 利用 [Bot Father](https://t.me/BotFather) 创建一个 Telegram Bot。

3. 创建并修改 `config.py`

   ```
   cp config.py.example config.py
   vim config.py
   ```

4. 构建并运行 Docker

   ```
   docker build -t nwpu-grade .
   docker run -d -e HTTPS_PROXY=<your proxy address> --name nwpu-grade nwpu-grade
   ```

## 测试脚本 client.py

本项目附带一个 client.py 方便 Scraper 的测试开发，使用 client.py 之前需要先在 config.py 中添加
`get_scraper` 函数。

```
python3 client.py
```

## 致谢

本项目受到了 @Dy1aNT 已经停止更新的项目 <https://github.com/Dy1aNT/NWPUgrade.git> 的启发。
