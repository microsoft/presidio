ARG REGISTRY=presidio.azurecr.io
FROM ${REGISTRY}/presidio-golang-base AS build-env

ARG NAME=presidio-recognizers-store
ARG PRESIDIOPATH=${GOPATH}/src/github.com/Microsoft/presidio
ARG VERSION=latest

WORKDIR ${PRESIDIOPATH}/${NAME}/cmd/${NAME}

RUN go clean

RUN GOOS=linux GOARCH=amd64 CGO_ENABLED=0 && go build -ldflags '-X github.com/Microsoft/presidio/pkg/version.Version=${VERSION}' -o /usr/bin/${NAME}

#----------------------------

FROM alpine:3.8

ARG NAME=presidio-recognizers-store

WORKDIR  /usr/bin/
COPY --from=build-env /usr/bin/${NAME} /usr/bin/
CMD  /usr/bin/presidio-recognizers-store