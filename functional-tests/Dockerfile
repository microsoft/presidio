# This dockerfile is used in CI to run golang based functional tests and
# output results as a junit report to a mounted volume where it can
# be read and published to ADO.
ARG REGISTRY=presidio.azurecr.io

FROM ${REGISTRY}/presidio-golang-base AS build-env


ARG PRESIDIOPATH=${GOPATH}/src/github.com/Microsoft/presidio

WORKDIR ${PRESIDIOPATH}

COPY ./functional-tests/ ./functional-tests

RUN  go get github.com/jstemmer/go-junit-report

CMD ["sh", "-x", "-c", "go test ./functional-tests --tags functional -count=1 -v 2>&1 | go-junit-report > /test-result-pipe/functional-report.xml "]