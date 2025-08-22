FROM python:3.12-slim

ARG NAME
ARG NLP_ENGINE=spacy
ARG ANALYZER_CONF_FILE=presidio_analyzer/conf/default_analyzer.yaml
ARG RECOGNIZER_REGISTRY_CONF_FILE=presidio_analyzer/conf/default_recognizers.yaml
ENV PIP_NO_CACHE_DIR=1

ARG NLP_CONF_FILE_DEFAULT=presidio_analyzer/conf/default.yaml
ARG NLP_CONF_FILE_TRANSFORMERS=presidio_analyzer/conf/transformers.yaml
ARG NLP_CONF_FILE=presidio_analyzer/conf/default.yaml
ENV NLP_CONF_FILE=${NLP_CONF_FILE}

ENV ANALYZER_CONF_FILE=${ANALYZER_CONF_FILE}
ENV RECOGNIZER_REGISTRY_CONF_FILE=${RECOGNIZER_REGISTRY_CONF_FILE}
ENV NLP_ENGINE=${NLP_ENGINE}

# Set runtime environment variables
ENV PORT=3000
ENV WORKERS=1

# Copy configuration files
COPY ${ANALYZER_CONF_FILE} /usr/bin/${NAME}/${ANALYZER_CONF_FILE}
COPY ${RECOGNIZER_REGISTRY_CONF_FILE} /usr/bin/${NAME}/${RECOGNIZER_REGISTRY_CONF_FILE}
COPY presidio_analyzer/conf/ /usr/bin/${NAME}/presidio_analyzer/conf/

WORKDIR /usr/bin/${NAME}

# Install system dependencies based on NLP engine requirements
RUN apt-get update && \
    apt-get install build-essential --no-install-recommends -y && \
    rm -rf /var/lib/apt/lists/

# Copy project configuration
COPY ./pyproject.toml /usr/bin/${NAME}/
# COPY ./README.md /usr/bin/${NAME}/

# Install Python dependencies based on NLP engine
RUN pip install poetry && \
    if [ "${NLP_ENGINE}" = "spacy" ]; then \
        poetry install --no-root --only=main -E server; \
    elif [ "${NLP_ENGINE}" = "transformers" ]; then \
        poetry install -E server -E transformers && \
        poetry add torch transformers huggingface_hub --no-lock; \
    elif [ "${NLP_ENGINE}" = "stanza" ]; then \
        poetry install --no-root --only=main -E server -E stanza; \
    fi

# Install NLP models - override config file for transformers if using default
COPY ./install_nlp_models.py /usr/bin/${NAME}/
RUN if [ "${NLP_ENGINE}" = "transformers" ] && [ "${NLP_CONF_FILE}" = "${NLP_CONF_FILE_DEFAULT}" ]; then \
        poetry run python install_nlp_models.py --conf_file "${NLP_CONF_FILE_TRANSFORMERS}"; \
    else \
        poetry run python install_nlp_models.py --conf_file "${NLP_CONF_FILE}"; \
    fi

# Copy application code
COPY . /usr/bin/${NAME}/

EXPOSE ${PORT}

CMD ["/bin/sh", "./start.sh"]
