FROM golang:1.11.3-alpine3.8

ARG DEP_VERSION="0.5.0"
    
RUN apk --update add curl git make g++ tesseract-ocr-dev

RUN curl -L -s https://github.com/golang/dep/releases/download/v${DEP_VERSION}/dep-linux-amd64 -o $GOPATH/bin/dep && \
    chmod +x $GOPATH/bin/dep && \
    curl -L https://git.io/vp6lP | sh

