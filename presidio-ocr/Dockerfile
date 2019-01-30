ARG REGISTRY=presidio.azurecr.io

FROM ${REGISTRY}/presidio-golang-base AS build-env

ARG NAME=presidio-ocr
ARG PRESIDIOPATH=${GOPATH}/src/github.com/Microsoft/presidio
ARG VERSION=latest

WORKDIR ${PRESIDIOPATH}/${NAME}/cmd/${NAME}
RUN GOOS=linux GOARCH=amd64 CGO_ENABLED=1 && go build -ldflags '-X github.com/Microsoft/presidio/pkg/version.Version=${VERSION}' -o /usr/bin/${NAME}

#----------------------------

FROM alpine:3.8

RUN apk --update add tesseract-ocr

ARG NAME=presidio-ocr
WORKDIR  /usr/bin/
COPY --from=build-env /usr/bin/${NAME} /usr/bin/
CMD  /usr/bin/presidio-ocr