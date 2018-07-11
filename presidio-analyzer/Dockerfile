FROM python:3.6.5-slim-stretch

WORKDIR /usr/bin/presidio-anaylzer

RUN apt-get update && apt-get install -y g++

ADD requirements.txt /usr/bin/presidio-anaylzer

RUN pip install -r requirements.txt

COPY . /usr/bin/presidio-anaylzer/

WORKDIR /usr/bin/presidio-anaylzer/analyzer
CMD python __main__.py