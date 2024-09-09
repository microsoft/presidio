#!/bin/bash

poetry install --no-interaction

# Perform different actions based on the value of MY_ENV_VAR
if [ "$DEV_MODE" == "transformers" ]; then
  poetry add torch transformers huggingface_hub
fi

poetry run python install_nlp_models.py --conf_file "$NLP_CONF_FILE"