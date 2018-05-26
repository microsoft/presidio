FROM python:3.6.5-alpine

RUN apk update && apk add --no-cache --virtual .build-deps build-base g++

WORKDIR /usr/bin/presidium-anaylzer
COPY . /usr/bin/presidium-anaylzer

RUN pip install -r requirements.txt && apk del .build-deps build-base g++

CMD python /usr/bin/presidium-anaylzer/anaylzer/__main__.py