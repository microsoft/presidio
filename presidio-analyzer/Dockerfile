ARG REGISTRY=presidio.azurecr.io
ARG PRESIDIO_DEPS_LABEL=latest
FROM ${REGISTRY}/presidio-python-deps:${PRESIDIO_DEPS_LABEL}

ARG NAME=presidio-analyzer
ARG PIP_EXTRA_INDEX_URL
ARG VERSION

WORKDIR /usr/bin/${NAME}
ENV PIP_EXTRA_INDEX_URL=${PIP_EXTRA_INDEX_URL}

RUN . $(pipenv --venv)/bin/activate && pip install presidio-analyzer==${VERSION:-0.0.1}    

#----------------------------

FROM ${REGISTRY}/presidio-python-deps:${PRESIDIO_DEPS_LABEL}

ARG NAME=presidio-analyzer
ADD ./${NAME}/analyzer /usr/bin/${NAME}/analyzer
WORKDIR /usr/bin/${NAME}/analyzer

CMD pipenv run python __main__.py serve --env-grpc-port