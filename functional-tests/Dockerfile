ARG REGISTRY=presidio.azurecr.io

FROM ${REGISTRY}/presidio-golang-base AS build-env


ARG PRESIDIOPATH=${GOPATH}/src/github.com/Microsoft/presidio

WORKDIR ${PRESIDIOPATH}

RUN  go get github.com/jstemmer/go-junit-report

COPY ./functional-tests ./functional-tests

CMD ["sh", "-x", "-c", "go test ./functional-tests --tags functional -count=1 -v 2>&1 | go-junit-report > report.xml ; cat ./report.xml ; mv ./report.xml /test-result-pipe/report.xml ; sleep 5"]