ARG REGISTRY=presidio.azurecr.io

FROM ${REGISTRY}/presidio-golang-base AS build-env


ARG PRESIDIOPATH=${GOPATH}/src/github.com/Microsoft/presidio

WORKDIR ${PRESIDIOPATH}

COPY ./tests ./tests

CMD ["sh", "-x", "-c", "go test ./tests --tags functional -count=1 -v"]