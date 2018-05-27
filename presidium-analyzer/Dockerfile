FROM python:3.6.5-slim-stretch

WORKDIR /usr/bin/presidium-anaylzer

RUN apt-get update && apt-get install -y g++

ADD requirements.txt /usr/bin/presidium-anaylzer

RUN pip install -r requirements.txt

COPY . /usr/bin/presidium-anaylzer/

CMD python analyzer/__main__.py