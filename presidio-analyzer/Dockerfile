FROM python:3.9-slim

ARG NAME
ARG NLP_CONF_FILE=presidio_analyzer/conf/default.yaml
ARG ANALYZER_CONF_FILE=presidio_analyzer/conf/default_analyzer.yaml
ARG RECOGNIZER_REGISTRY_CONF_FILE=presidio_analyzer/conf/default_recognizers.yaml
ENV PIPENV_VENV_IN_PROJECT=1
ENV PIP_NO_CACHE_DIR=1

ENV ANALYZER_CONF_FILE=${ANALYZER_CONF_FILE}
ENV RECOGNIZER_REGISTRY_CONF_FILE=${RECOGNIZER_REGISTRY_CONF_FILE}
ENV NLP_CONF_FILE=${NLP_CONF_FILE}

COPY ${ANALYZER_CONF_FILE} /usr/bin/${NAME}/${ANALYZER_CONF_FILE}
COPY ${RECOGNIZER_REGISTRY_CONF_FILE} /usr/bin/${NAME}/${RECOGNIZER_REGISTRY_CONF_FILE}
COPY ${NLP_CONF_FILE} /usr/bin/${NAME}/${NLP_CONF_FILE}

WORKDIR /usr/bin/${NAME}

COPY ./Pipfile* /usr/bin/${NAME}/

# Install essential build tools
RUN apt-get update \
  && apt-get install -y build-essential

RUN pip install pipenv \
  && pipenv install --deploy
# install nlp models specified in NLP_CONF_FILE
COPY ./install_nlp_models.py /usr/bin/${NAME}/

RUN pipenv run python install_nlp_models.py --conf_file ${NLP_CONF_FILE}

COPY . /usr/bin/${NAME}/
EXPOSE ${PORT}
CMD pipenv run python app.py --host 0.0.0.0
