ARG REGISTRY=presidio.azurecr.io
ARG NAME=presidio-analyzer

FROM ${REGISTRY}/presidio-python-deps

WORKDIR /usr/bin/${NAME}
ADD ./${NAME} /usr/bin/${NAME}

RUN pip install --no-cache-dir -r requirements-dev.txt && \
    flake8 analyzer --exclude "*pb2*.py" && \
    pytest --log-cli-level=0

#----------------------------

FROM ${REGISTRY}/presidio-python-deps

ADD ./${NAME}/analyzer /usr/bin/${NAME}/analyzer
WORKDIR /usr/bin/${NAME}/analyzer

CMD python __main__.py serve --env-grpc-port