#!/usr/bin/env bash
set -euo pipefail

cd /Volumes/external_ssd/source/forked_presidio/presidio/presidio-analyzer

export ANALYZER_CONF_FILE=presidio_analyzer/conf/gliner_edge_analyzer.yaml
export NLP_CONF_FILE=presidio_analyzer/conf/gliner_edge_nlp.yaml
export RECOGNIZER_REGISTRY_CONF_FILE=presidio_analyzer/conf/gliner_edge_recognizers.yaml
export PORT="${PORT:-3000}"
export WORKERS="${WORKERS:-1}"

poetry run python app.py
