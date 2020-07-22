# Presidio Analyzer Dockerfile. 
# This dockerfile installs presidio analyzer wheel from a pypi endpoint.
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
ADD ./${NAME}/presidio_analyzer /usr/bin/${NAME}/presidio_analyzer
ADD ./${NAME}/conf /usr/bin/${NAME}/presidio_analyzer/conf
WORKDIR /usr/bin/${NAME}/presidio_analyzer

CMD pipenv run python app.py serve --env-grpc-port
