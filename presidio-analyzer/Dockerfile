FROM python:3.7-alpine

ARG NAME=presidio-analyzer

COPY ./${NAME}/requirements.txt /usr/bin/${NAME}/requirements.txt
WORKDIR /usr/bin/${NAME}

ARG re2_version="2018-08-01"
ARG pyre2_ver="0.2.23"

RUN apk update && \
    apk upgrade && \
    apk add --no-cache g++ && \
    apk add --no-cache --virtual=build_deps make tar wget gfortran && \
    wget -O re2.tar.gz https://github.com/google/re2/archive/${re2_version}.tar.gz && \
    mkdir re2 && tar --extract --file "re2.tar.gz" --directory "re2" --strip-components 1 && \
    cd re2 && make install && cd .. && rm -rf re2 && rm re2.tar.gz && \
    pip install --no-cache-dir -r requirements.txt && \
    # Fork of https://github.com/andreasvc/pyre2
    pip install --no-cache-dir https://github.com/torosent/pyre2/archive/release/${pyre2_ver}.zip && \ 
    apk del build_deps

ADD ./${NAME}/analyzer /usr/bin/${NAME}/analyzer
WORKDIR /usr/bin/${NAME}/analyzer
CMD python __main__.py serve --env-grpc-port