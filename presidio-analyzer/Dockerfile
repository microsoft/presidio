FROM python:3.6.5-slim-stretch

ARG NAME=presidio-analyzer

RUN apt-get update && apt-get install -y g++

ADD ./${NAME} /usr/bin/${NAME}

WORKDIR /usr/bin/${NAME}
RUN pip install -r requirements.txt

WORKDIR /usr/bin/${NAME}/analyzer
CMD python __main__.py