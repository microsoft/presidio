ARG REGISTRY=presidio.azurecr.io

FROM ${REGISTRY}/presidio-golang-base AS build-env

ARG NAME=presidio-ocr
ARG PRESIDIOPATH=${GOPATH}/src/github.com/Microsoft/presidio
ARG VERSION=latest

WORKDIR ${PRESIDIOPATH}/${NAME}/cmd/${NAME}
RUN GOOS=linux GOARCH=amd64 CGO_ENABLED=0 && go build -ldflags '-X github.com/Microsoft/presidio/pkg/version.Version=${VERSION}' -o /usr/bin/${NAME}

#----------------------------

FROM alpine:3.8

RUN apk add 'icu-libs' --update-cache --repository http://nl.alpinelinux.org/alpine/edge/main
RUN apk add 'tesseract-ocr>=4.0.0' --update-cache --repository http://nl.alpinelinux.org/alpine/edge/community

ARG NAME=presidio-ocr
WORKDIR  /usr/bin/
COPY --from=build-env /usr/bin/${NAME} /usr/bin/
CMD  /usr/bin/presidio-ocr