# Presidio - Data Protection and Anonymization API

**Context aware, pluggable and customizable PII anonymization service for text and images.**

## What is Presidio

Presidio _(Origin from Latin praesidium ‘protection, garrison’)_ helps to ensure sensitive data is properly managed and governed. It provides fast **_identification_** and **_anonymization_** modules for private entities in text such as credit card numbers, names, locations, social security numbers, bitcoin wallets, US phone numbers, financial data and more.

### Goals

- Allow organizations to preserve privacy in a simpler way by democratizing de-identification technologies and introducing transparency in decisions.
- Embrace extensibility and customizability to a specific business need.
- Facilitate both fully automated and semi-automated PII de-identification flows on multiple platforms.

### Main features

1. **Predefined** or **custom PII recognizers** leveraging *Named Entity Recognition*, *regular expressions*, *rule based logic* and *checksum* with relevant context in multiple languages.
2. Options for connecting to external PII detection models.
3. Multiple usage options, **from Python or PySpark workloads through Docker to Kubernetes**.
4. **Customizability** in PII identification and anonymization.
5. Module for **redacting PII text in images**.

:warning: Presidio can help identify sensitive/PII data in un/structured text. However, because Presidio is using trained ML models, there is no guarantee that Presidio will find all sensitive information. Consequently, additional systems and protections should be employed.

## Demo

[Try Presidio with your own data](https://aka.ms/presidio-demo)

## Overview

<p align="center">
  <kbd>  
  <img width="-100" height="-50" src="assets/presidio_gif.gif">
  </kbd>
</p>

## Installing Presidio

1. [Using pip](installation.md#using-pip)
2. [Using Docker](installation.md#using-docker)

## Running Presidio

1. [Running Presidio via code](deployment-samples/python/index.md)
2. [Running Presidio via HTTP](deployment-samples/docker/index.md)
2. [Setting up a development environment](development.md)
3. [Perform PII identification using presidio-analyzer](analyzer/index.md)
4. [Perform PII anonymization using presidio-anonymizer](anonymizer/index.md)
5. [Perform PII identification and anonymization in images using presidio-image-anonymizer](image-anonymizer/index.md)
6. [Example deployments](deployment-samples/index.md)

## Support

- Before you submit an issue, please go over the [documentation](docs/readme.md). For general discussions, please use the [Github repo's discussion board](https://github.com/microsoft/presidio/discussions).
- If you have a usage question, found a bug or have a suggestion for improvement, please file a [Github issue](https://github.com/microsoft/presidio/issues).
- For other matters, please email [presidio@microsoft.com](mailto:presidio@microsoft.com).
