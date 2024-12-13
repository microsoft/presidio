FROM python:3.10-slim

ARG NAME
ARG NLP_CONF_FILE
ARG ANALYZER_CONF_FILE
ARG RECOGNIZER_REGISTRY_CONF_FILE
ENV PIP_NO_CACHE_DIR=1

ENV ANALYZER_CONF_FILE=${ANALYZER_CONF_FILE}
ENV RECOGNIZER_REGISTRY_CONF_FILE=${RECOGNIZER_REGISTRY_CONF_FILE}
ENV NLP_CONF_FILE=${NLP_CONF_FILE}

ENV PORT=3000
ENV WORKERS=1

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

COPY ./pyproject.toml /usr/bin/${NAME}/
COPY ./README.md /usr/bin/${NAME}/
RUN pip install poetry && poetry install --no-root --only=main -E server

COPY . /usr/bin/${NAME}/
EXPOSE ${PORT}
CMD poetry run gunicorn -w $WORKERS -b 0.0.0.0:$PORT 'app:create_app()'