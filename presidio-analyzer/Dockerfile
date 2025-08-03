FROM python:3.12-slim

# Arguments
ARG NAME
ARG NLP_CONF_FILE=presidio_analyzer/conf/default.yaml
ARG ANALYZER_CONF_FILE=presidio_analyzer/conf/default_analyzer.yaml
ARG RECOGNIZER_REGISTRY_CONF_FILE=presidio_analyzer/conf/default_recognizers.yaml

# Environment Variables
ENV PIP_NO_CACHE_DIR=1
ENV ANALYZER_CONF_FILE=${ANALYZER_CONF_FILE}
ENV RECOGNIZER_REGISTRY_CONF_FILE=${RECOGNIZER_REGISTRY_CONF_FILE}
ENV NLP_CONF_FILE=${NLP_CONF_FILE}
ENV PORT=3000
ENV WORKERS=1

# System deps & security upgrades
RUN apt-get update \
  && apt-get dist-upgrade -y \
  && apt-get install -y --no-install-recommends build-essential \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd --create-home --shell /bin/bash presidio

# Set working directory
WORKDIR /home/presidio/app

# Set ownership early so COPYed files inherit correct permissions
RUN mkdir -p /home/presidio/app && chown -R presidio:presidio /home/presidio

# Switch to non-root user
USER presidio

# Copy config files
COPY --chown=presidio:presidio ${ANALYZER_CONF_FILE} ./${ANALYZER_CONF_FILE}
COPY --chown=presidio:presidio ${RECOGNIZER_REGISTRY_CONF_FILE} ./${RECOGNIZER_REGISTRY_CONF_FILE}
COPY --chown=presidio:presidio ${NLP_CONF_FILE} ./${NLP_CONF_FILE}

# Copy poetry config files
COPY --chown=presidio:presidio pyproject.toml README.md ./

# Install Poetry and dependencies
RUN pip install --no-cache-dir poetry \
  && poetry install --no-root --only=main -E server

# Install NLP models
COPY --chown=presidio:presidio install_nlp_models.py ./
RUN poetry run python install_nlp_models.py --conf_file ${NLP_CONF_FILE}

# Copy full app source
COPY --chown=presidio:presidio . .

# Expose port
EXPOSE ${PORT}

# Run the server
CMD ["poetry", "run", "gunicorn", "-w", "${WORKERS}", "-b", "0.0.0.0:${PORT}", "app:create_app()"]
