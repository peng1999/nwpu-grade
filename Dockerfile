FROM alpine:edge

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.sjtug.sjtu.edu.cn/g' /etc/apk/repositories \
 && sed -i -e 's/v[[:digit:]]\..*\//edge\//g' /etc/apk/repositories \
 && apk add --no-cache py3-pip \
 && pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple pip -U \
 && python3 -m pip config set \
    global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

RUN apk add --update --no-cache gcc \
    python3-dev musl-dev libffi-dev openssl-dev \
 && python3 -m pip install poetry

COPY . /opt/nwpu-grade/

WORKDIR /opt/nwpu-grade

RUN apk add --update --no-cache \
    libxml2-dev libxslt-dev \
 && poetry install

CMD poetry run python3 launch_bot.py
