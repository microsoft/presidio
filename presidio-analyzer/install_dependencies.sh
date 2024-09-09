#!/bin/bash

poetry install --no-interaction

if [ "$DEV_MODE" == "transformers" ]; then
  poetry add torch transformers huggingface_hub
fi

poetry run python install_nlp_models.py --conf_file "$NLP_CONF_FILE"