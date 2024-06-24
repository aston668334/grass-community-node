FROM python:3.9-alpine as base
FROM base as builder

RUN apk update && apk add nano curl net-tools iputils python3 py3-pip

WORKDIR /opt
RUN mkdir app

COPY /requirements.txt app
COPY /grass_community_proxy.py app
COPY /grass_community_no_proxy.py app

WORKDIR /opt/app

RUN pip install --no-cache-dir -r requirements.txt

ENV GRASS_USERID=${GRASS_USERID}
CMD [ "python3", "grass_community_no_proxy.py" ]
