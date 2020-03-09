ARG REGISTRY=presidio.azurecr.io

FROM ${REGISTRY}/presidio-golang-base AS build-env


ARG PRESIDIOPATH=${GOPATH}/src/github.com/Microsoft/presidio

WORKDIR ${PRESIDIOPATH}

COPY ./functional-tests/ /usr/bin/functional-tests

#----------------------------

FROM golang:1.11.3-alpine3.8

ARG NAME=functional-tests
WORKDIR  /usr/bin/
COPY --from=build-env /usr/bin/functional-tests /usr/bin/functional-tests
RUN ls /usr/bin/functional-tests

RUN apk update && apk upgrade && \
    apk add --no-cache bash git openssh
RUN  go get github.com/jstemmer/go-junit-report

CMD ["sh", "-x", "-c", "go test ./functional-tests --tags functional -count=1 -v 2>&1 | go-junit-report > /test-result-pipe/report.xml "]