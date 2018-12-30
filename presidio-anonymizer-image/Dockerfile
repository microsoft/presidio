ARG REGISTRY=presidio.azurecr.io

FROM ${REGISTRY}/presidio-golang-base AS build-env

ARG NAME=presidio-anonymizer-image
ARG PRESIDIOPATH=${GOPATH}/src/github.com/Microsoft/presidio
ARG VERSION=latest

RUN apk --update add imagemagick --repository=http://dl-cdn.alpinelinux.org/alpine/edge/main

WORKDIR ${PRESIDIOPATH}/${NAME}/cmd/${NAME}
RUN GOOS=linux GOARCH=amd64 CGO_ENABLED=0 && go build -ldflags '-X github.com/Microsoft/presidio/pkg/version.Version=${VERSION}' -o /usr/bin/${NAME}

#----------------------------

FROM alpine:3.8

RUN apk --update add imagemagick --repository=http://dl-cdn.alpinelinux.org/alpine/edge/main

ARG NAME=presidio-anonymizer-image
WORKDIR  /usr/bin/
COPY --from=build-env /usr/bin/${NAME} /usr/bin/
CMD  /usr/bin/${NAME}