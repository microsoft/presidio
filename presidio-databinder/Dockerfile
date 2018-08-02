FROM alpine:3.7

RUN apk add --no-cache --update ca-certificates

COPY rootfs/presidio-databinder /usr/bin/presidio-databinder

CMD /usr/bin/presidio-databinder