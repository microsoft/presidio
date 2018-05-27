FROM centos:7

RUN yum -y install \
    git \
    lsof \
    make \
    mercurial \
    wget \
    && yum clean all

ENV goversion 1.9.2
ENV gofile go${goversion}.linux-amd64.tar.gz
ENV gourl https://storage.googleapis.com/golang/${gofile}

RUN wget -q -O /usr/local/${gofile} ${gourl} \
  && mkdir /usr/local/go \
  && tar -xzf /usr/local/${gofile} -C /usr/local/go --strip 1

CMD cd /mnt/src/github.com/graymeta/stow && GOPATH=/mnt PATH=/usr/local/go/bin:$GOPATH/bin:$PATH make test
