FROM python:3.7.1-alpine3.8

ARG re2_version="2018-12-01"
ARG NAME=presidio-analyzer
COPY ./${NAME}/Pipfile /usr/bin/${NAME}/Pipfile
COPY ./${NAME}/Pipfile.lock /usr/bin/${NAME}/Pipfile.lock

WORKDIR /usr/bin/${NAME}

RUN apk --update add --no-cache g++ && \
    apk --update add --no-cache --virtual build_deps make tar wget clang && \
    wget -O re2.tar.gz https://github.com/google/re2/archive/${re2_version}.tar.gz && \
    mkdir re2 && tar --extract --file "re2.tar.gz" --directory "re2" --strip-components 1 && \
    cd re2 && make install && cd .. && rm -rf re2 && rm re2.tar.gz && \
    apk add --virtual build_deps make automake gcc g++ subversion python3-dev

# Making sure we have pipenv
RUN pip3 install pipenv
# Updating setuptools
RUN pip3 install --upgrade setuptools
# Installing specified packages from Pipfile.lock
RUN pipenv sync
# Print to screen the installed packages for easy debugging
RUN pipenv run pip freeze

RUN apk del build_deps
