#!/bin/bash

pip install --require-hashes --no-deps presidio-analyzer==2.2.361 \
    --hash=sha256:7054b36303f5f47dd4bb3b00600bc936fb46aa3cc5e6befde3de839f0205f7f2
pip install --require-hashes --no-deps presidio-anonymizer==2.2.361 \
    --hash=sha256:ff0f64c234aa7ac37042cf7f187ed4a47587cff65418304d716af7d194c96ed3
pip install --require-hashes --no-deps azure-storage-blob==12.25.0 \
    --hash=sha256:a38e18bf10258fb19028f343db0d3d373280c6427a619c98c06d76485805b755
python -m spacy download en_core_web_lg