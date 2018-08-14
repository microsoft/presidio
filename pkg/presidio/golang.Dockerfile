FROM golang:1.10-alpine3.8

WORKDIR /root/librdkafka

RUN apk add --no-cache g++ openssl pkgconfig
RUN apk add --no-cache --virtual=build_deps \
    ca-certificates \
    tar \
    bash \
    openssl-dev \
    make \
    musl-dev \
    zlib-dev \
    python && \
    mkdir -p /root/librdkafka && \
    wget -O "librdkafka.tar.gz" "https://github.com/edenhill/librdkafka/archive/v0.11.5.tar.gz" && \ 
    mkdir -p librdkafka && \ 
    tar \
    --extract \
    --file "librdkafka.tar.gz" \
    --directory "librdkafka" \
    --strip-components 1 && \
    cd "librdkafka" && \
    ./configure --prefix=/usr && \
    make -j "$(getconf _NPROCESSORS_ONLN)" && \
    make install && \
    rm -rf /root/librdkafka && \
    apk del build_deps

RUN mkdir /lib64 && ln -s /lib/libc.musl-x86_64.so.1 /lib64/ld-linux-x86-64.so.2