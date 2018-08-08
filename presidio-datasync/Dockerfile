FROM presidio-golang AS build-env

ARG NAME=presidio-datasync
ARG PRESIDIOPATH=${GOPATH}/src/github.com/Microsoft/presidio
ARG VERSION=latest

ADD ./${NAME} ${PRESIDIOPATH}/${NAME}
ADD ./vendor ${PRESIDIOPATH}/vendor
ADD ./pkg ${PRESIDIOPATH}/pkg

WORKDIR ${PRESIDIOPATH}/${NAME}/cmd/${NAME}
RUN GOOS=linux GOARCH=amd64 CGO_ENABLED=1 && go build -a -installsuffix cgo -ldflags '-X github.com/Microsoft/presidio/pkg/version.Version=${VERSION}' -o /usr/bin/${NAME}

#----------------------------

FROM presidio-alpine

RUN apk add --no-cache --update ca-certificates

ARG NAME=presidio-datasync

WORKDIR  /usr/bin/
COPY --from=build-env /usr/bin/${NAME} /usr/bin/
CMD  /usr/bin/presidio-datasync