FROM python:3.7.7-alpine

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories

WORKDIR /app

COPY requirements.txt .

RUN apk add --no-cache build-base && \
    pip install --no-cache-dir -r requirements.txt -i https://pypi.douban.com/simple && \
    apk del build-base && \
    apk add --no-cache libstdc++

COPY main.py .

ENTRYPOINT [ "python", "./main.py" ]