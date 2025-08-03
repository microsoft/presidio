FROM python:3.12-slim

# Arguments
ARG NAME
ARG NLP_CONF_FILE=presidio_analyzer/conf/default.yaml
ARG ANALYZER_CONF_FILE=presidio_analyzer/conf/default_analyzer.yaml
ARG RECOGNIZER_REGISTRY_CONF_FILE=presidio_analyzer/conf/default_recognizers.yaml

# Environment
ENV PIP_NO_CACHE_DIR=1
ENV PORT=3000
ENV WORKERS=1
ENV PATH="/home/presidio/.local/bin:$PATH"
ENV ANALYZER_CONF_FILE=${ANALYZER_CONF_FILE}
ENV RECOGNIZER_REGISTRY_CONF_FILE=${RECOGNIZER_REGISTRY_CONF_FILE}
ENV NLP_CONF_FILE=${NLP_CONF_FILE}

# Install system dependencies
RUN apt-get update && apt-get dist-upgrade -y && apt-get install -y --no-install-recommends \
    build-essential curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Add non-root user
RUN useradd --create-home --shell /bin/bash presidio
USER presidio
WORKDIR /home/presidio/app

# Install Poetry (user-local)
RUN pip install --user poetry

# Copy the pyproject.toml BEFORE any poetry commands
COPY --chown=presidio:presidio pyproject.toml README.md ./

# Configure Poetry
RUN poetry config virtualenvs.in-project true \
 && poetry env use python

# Copy required config files
COPY --chown=presidio:presidio ${ANALYZER_CONF_FILE} ./${ANALYZER_CONF_FILE}
COPY --chown=presidio:presidio ${RECOGNIZER_REGISTRY_CONF_FILE} ./${RECOGNIZER_REGISTRY_CONF_FILE}
COPY --chown=presidio:presidio ${NLP_CONF_FILE} ./${NLP_CONF_FILE}

# Install dependencies
RUN poetry install --no-root --only=main -E server

# Copy remaining source files
COPY --chown=presidio:presidio . .

# Install NLP models (if needed)
RUN poetry run python install_nlp_models.py --conf_file ${NLP_CONF_FILE}

EXPOSE ${PORT}
CMD ["poetry", "run", "gunicorn", "-w", "${WORKERS}", "-b", "0.0.0.0:${PORT}", "app:create_app()"]
