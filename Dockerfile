FROM node AS builder

WORKDIR /app

COPY ./web_app/ .

RUN npm config set registry https://registry.npmmirror.com \
     && npm install \
     && npm run build 

FROM python:3.8-slim

WORKDIR /app

COPY ./auto_sign.py ./web_app.py ./requirements.txt ./
COPY ./template ./template
COPY ./api ./api
COPY --from=builder /app/build ./web_app/build

RUN pip config set global.index-url http://mirrors.aliyun.com/pypi/simple/ \
    && pip install --trusted-host mirrors.aliyun.com -r requirements.txt

CMD [ "python","auto_sign.py"]
