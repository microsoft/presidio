FROM python:3.6.5-slim-stretch

ARG NAME=presidio-analyzer

RUN apt-get update && apt-get install -y g++ && rm -rf /var/lib/apt/lists/*

ADD ./${NAME} /usr/bin/${NAME}

WORKDIR /usr/bin/${NAME}
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /usr/bin/${NAME}/analyzer
CMD python __main__.py