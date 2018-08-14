FROM golang:1.10-alpine AS build-env

ARG NAME=presidio-api
ARG PRESIDIOPATH=${GOPATH}/src/github.com/Microsoft/presidio
ARG VERSION=latest

ADD ./${NAME} ${PRESIDIOPATH}/${NAME}
ADD ./vendor ${PRESIDIOPATH}/vendor
ADD ./pkg ${PRESIDIOPATH}/pkg

WORKDIR ${PRESIDIOPATH}/${NAME}/cmd/${NAME}
RUN GOOS=linux GOARCH=amd64 CGO_ENABLED=0 && go build -ldflags '-X github.com/Microsoft/presidio/pkg/version.Version=${VERSION}' -o /usr/bin/${NAME}

#----------------------------

FROM alpine:3.8

ARG NAME=presidio-api
WORKDIR  /usr/bin/
COPY --from=build-env /usr/bin/${NAME} /usr/bin/
CMD  /usr/bin/presidio-api