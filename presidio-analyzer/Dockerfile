FROM python:3.7-alpine

ARG NAME=presidio-analyzer

COPY ./${NAME}/requirements.txt /usr/bin/${NAME}/requirements.txt
WORKDIR /usr/bin/${NAME}

RUN apk update && \
    apk upgrade && \
    apk add --no-cache g++ && \
    apk add --no-cache --virtual=build_deps make git gfortran && \
    git clone https://github.com/google/re2.git && cd re2 && make install && cd .. && rm -rf re2 && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir git+https://github.com/andreasvc/pyre2.git && \
    apk del build_deps

ADD ./${NAME}/analyzer /usr/bin/${NAME}/analyzer
WORKDIR /usr/bin/${NAME}/analyzer
CMD python __main__.py serve --env-grpc-port