FROM python:3.13-slim

ARG NLP_CONF_FILE
ARG ANALYZER_CONF_FILE
ARG RECOGNIZER_REGISTRY_CONF_FILE
ENV PIP_NO_CACHE_DIR=1

ENV ANALYZER_CONF_FILE=${ANALYZER_CONF_FILE}
ENV RECOGNIZER_REGISTRY_CONF_FILE=${RECOGNIZER_REGISTRY_CONF_FILE}
ENV NLP_CONF_FILE=${NLP_CONF_FILE}

ENV PORT=3000
ENV WORKERS=1

COPY ${ANALYZER_CONF_FILE} /app/${ANALYZER_CONF_FILE}
COPY ${RECOGNIZER_REGISTRY_CONF_FILE} /app/${RECOGNIZER_REGISTRY_CONF_FILE}
COPY ${NLP_CONF_FILE} /app/${NLP_CONF_FILE}

WORKDIR /app

RUN apt-get update \
  && apt-get install build-essential tesseract-ocr ffmpeg libsm6 libxext6 --no-install-recommends -y \
  && rm -rf /var/lib/apt/lists/* \
  && tesseract -v

COPY ./pyproject.toml /app/
RUN pip install poetry && poetry install --no-root --only=main -E server

COPY . /app/
EXPOSE ${PORT}
CMD ["./entrypoint.sh"]
