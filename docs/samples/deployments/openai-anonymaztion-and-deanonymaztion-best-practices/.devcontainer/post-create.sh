#!/bin/bash

pip install --upgrade pip
python -m spacy download en_core_web_lg

cd src/api
pip install -r requirements.txt

# Installing kubectl
curl -sSL -o /usr/local/bin/kubectl https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl \
    && chmod +x /usr/local/bin/kubectl
