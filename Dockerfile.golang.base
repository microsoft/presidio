ARG REGISTRY=presidio.azurecr.io
ARG PRESIDIO_DEPS_LABEL=latest

FROM ${REGISTRY}/presidio-golang-deps:${PRESIDIO_DEPS_LABEL}

WORKDIR $GOPATH/src/github.com/Microsoft/presidio
ADD . $GOPATH/src/github.com/Microsoft/presidio

RUN dep ensure
RUN make go-test