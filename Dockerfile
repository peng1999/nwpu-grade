FROM python:3.9-slim

# change mirrors
RUN sed -i "s/deb.debian.org/mirrors.aliyun.com/g" /etc/apt/sources.list  \
 && sed -i "s/security.debain.org/mirrors.aliyun.com/g" /etc/apt/sources.list \
 && rm -Rf /etc/apt/sources.list.d/* \
 && rm -Rf /var/lib/apt/lists/* \
 && pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple pip -U \
 && python3 -m pip config set \
    global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

RUN python3 -m pip install poetry

COPY . /opt/nwpu-grade/

WORKDIR /opt/nwpu-grade

RUN poetry install

CMD poetry run python3 launch_bot.py
