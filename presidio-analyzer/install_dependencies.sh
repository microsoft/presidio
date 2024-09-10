#!/bin/bash

poetry install -E server ${POETRY_EXTRAS} --no-interaction

poetry run python install_nlp_models.py --conf_file "$NLP_CONF_FILE"