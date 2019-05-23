ARG REGISTRY=presidio.azurecr.io
ARG PRESIDIO_DEPS_LABEL=latest	

FROM ${REGISTRY}/presidio-python-deps:${PRESIDIO_DEPS_LABEL}	

ARG NAME=presidio-analyzer
WORKDIR /usr/bin/${NAME}
ADD ./${NAME} /usr/bin/${NAME}

RUN pipenv install --dev --sequential && \
    pipenv run pylint analyzer && \
    pipenv run flake8 analyzer --exclude "*pb2*.py" && \
	pipenv run pytest --log-cli-level=0

#----------------------------

FROM ${REGISTRY}/presidio-python-deps

ARG NAME=presidio-analyzer
ADD ./${NAME}/analyzer /usr/bin/${NAME}/analyzer
WORKDIR /usr/bin/${NAME}/analyzer

CMD pipenv run python __main__.py serve --env-grpc-port