FROM alpine:3.7

RUN apk add --no-cache --update ca-certificates

COPY rootfs/presidio-scanner /usr/bin/presidio-scanner

CMD /usr/bin/presidio-scanner