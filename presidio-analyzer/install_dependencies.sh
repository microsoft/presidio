#!/bin/bash

if [ "$DEV_MODE" == "transformers" ]; then
  poetry install -E server -E transformers --no-interaction
else
  poetry install -E server --no-interaction
fi

poetry run python install_nlp_models.py --conf_file "$NLP_CONF_FILE"