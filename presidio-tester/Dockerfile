ARG REGISTRY=presidio.azurecr.io

FROM ${REGISTRY}/presidio-golang-base AS build-env

ARG NAME=presidio-tester
ARG PRESIDIOPATH=${GOPATH}/src/github.com/Microsoft/presidio
ARG VERSION=latest


WORKDIR ${PRESIDIOPATH}/${NAME}/cmd/${NAME}
RUN GOOS=linux GOARCH=amd64 CGO_ENABLED=0 && go build -ldflags '-X github.com/Microsoft/presidio/pkg/version.Version=${VERSION}' -o /usr/bin/${NAME}
RUN cp -r ${PRESIDIOPATH}/${NAME}/cmd/${NAME}/testdata /usr/bin/testdata

#----------------------------

FROM alpine:3.8

ARG NAME=presidio-tester
WORKDIR  /usr/bin/
COPY --from=build-env /usr/bin/${NAME} /usr/bin/
COPY --from=build-env /usr/bin/testdata /usr/bin/testdata

CMD  /usr/bin/presidio-tester