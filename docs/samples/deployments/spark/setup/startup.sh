#!/bin/bash

pip install presidio-analyzer==2.2.361
pip install presidio-anonymizer==2.2.361
pip install azure-storage-blob==12.25.0
python -m spacy download en_core_web_lg