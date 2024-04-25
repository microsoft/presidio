FROM python:3.9-slim

ARG NAME
ARG NLP_CONF_FILE
ARG ANALYZER_CONF_FILE
ARG RECOGNIZER_REGISTRY_CONF_FILE
ENV PIPENV_VENV_IN_PROJECT=1
ENV PIP_NO_CACHE_DIR=1

ENV ANALYZER_CONF_FILE=${ANALYZER_CONF_FILE}
ENV RECOGNIZER_REGISTRY_CONF_FILE=${RECOGNIZER_REGISTRY_CONF_FILE}
ENV NLP_CONF_FILE=${NLP_CONF_FILE}

COPY ${ANALYZER_CONF_FILE} /usr/bin/${NAME}/${ANALYZER_CONF_FILE}
COPY ${RECOGNIZER_REGISTRY_CONF_FILE} /usr/bin/${NAME}/${RECOGNIZER_REGISTRY_CONF_FILE}
COPY ${NLP_CONF_FILE} /usr/bin/${NAME}/${NLP_CONF_FILE}

WORKDIR /usr/bin/${NAME}

# Install essential build tools
RUN apt-get update \
  && apt-get install -y build-essential

# install tesseract and other image related dependencies
RUN apt-get update \
  && apt-get install tesseract-ocr -y \
  && rm -rf /var/lib/apt/lists/* \
  && tesseract -v

RUN apt-get update  \
  && apt-get install ffmpeg libsm6 libxext6  -y


COPY ./Pipfile* /usr/bin/${NAME}/
RUN pip install pipenv \
  && pipenv install --deploy

COPY . /usr/bin/${NAME}/
EXPOSE ${PORT}
CMD pipenv run python app.py