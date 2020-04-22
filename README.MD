# Presidio - Data protection and anonymization API

**Context aware, pluggable and customizable PII anonymization service for text and images.**

---

[![Build Status](https://dev.azure.com/csedevil/Presidio/_apis/build/status/Presidio-CI/Presidio-CI?branchName=master&jobName=BuildAndPushPresidioMaster)](https://dev.azure.com/csedevil/Presidio/_build/latest?definitionId=129&branchName=master)
[![Go Report Card](https://goreportcard.com/badge/github.com/Microsoft/presidio)](https://goreportcard.com/report/github.com/Microsoft/presidio)
[![MIT license](https://img.shields.io/badge/license-MIT-brightgreen.svg)](http://opensource.org/licenses/MIT)
![Release](https://img.shields.io/github/release/Microsoft/presidio.svg)

## What is Presidio

Presidio _(Origin from Latin praesidium ‘protection, garrison’)_ helps to ensure sensitive text is properly managed and governed. It provides fast **_analytics_** and **_anonymization_** for sensitive text such as credit card numbers, names, locations, social security numbers, bitcoin wallets, US phone numbers and financial data.
Presidio analyzes the text using predefined or custom recognizers to identify entities, patterns, formats, and checksums with relevant context. Presidio leverages docker and kubernetes for workloads at scale.

Presidio can be integrated into any data pipeline for intelligent PII scrubbing. It is open-source, transparent and scalable. Additionally, PII anonymization use-cases often require a different set of PII entities to be detected, some of which are domain or business specific. Presidio allows you to **customize or add new PII recognizers** via API or code to best fit your anonymization needs.

:warning: Presidio can help identify sensitive/PII data in un/structured text. However, because Presidio is using trained ML models, there is no guarantee that Presidio will find all sensitive information. Consequently, additional systems and protections should be employed.

[Presidio Features](docs/overview.md#features)

[Presidio Input and output](docs/overview.md#input-and-output)

## Demo

[Try Presidio with your own data](https://aka.ms/presidio-demo)

## Learn more

More information can be found in the [Presidio documentation](https://microsoft.github.io/presidio/).

- [Architecture](docs/design.md)
- [API Samples](docs/samples.md)
- [Supported field types](docs/field_types.md)
- [Database and storage scanner](docs/tutorial_scheduler.md)
- [Adding new PII recognizers](docs/custom_fields.md)
- [Generating Swagger file](presidio-api/cmd/presidio-api/docs/readme.md)
- [Evaluating Presidio](https://github.com/microsoft/presidio-research)

## Deploying Presidio

[Deploy Presidio as a system](docs/deploy.md):

- [Install locally using Docker](docs/deploy.md#the-easy-way-with-docker)
- [Presidio As a Service with Kubernetes](docs/deploy.md#presidio-as-a-service-with-kubernetes)
- [presidio-analyzer as a standalone python package](docs/deploy.md#install-presidio-analyzer-as-a-python-package)

## Developing Presidio

- [Setting up a development environment](docs/development.md)
- [Run locally with KIND (Kubernetes in Docker)](docs/KIND.md)

## Technology Stack

Presidio leverages:

- [Kubernetes](https://kubernetes.io/)
- [spaCy](https://spacy.io/)
- [Redis](https://redis.io/)
- [GRPC](https://grpc.io)
- [re2](https://github.com/google/re2)

## Current input/output components status

| Module            | Feature              | Status             |
| ----------------- | -------------------- | ------------------ |
| API               | HTTP input           | :white_check_mark: |
| Scanner           | MySQL                | :x:                |
| Scanner           | MSSQL                | :x:                |
| Scanner           | PostgreSQL           | :x:                |
| Scanner           | Oracle               | :x:                |
| Scanner           | Azure Blob Storage   | :white_check_mark: |
| Scanner           | S3                   | :white_check_mark: |
| Scanner           | Google Cloud Storage | :x:                |
| Streams           | Kafka                | :white_check_mark: |
| Streams           | Azure Event Hub      | :white_check_mark: |
| Datasink (output) | MySQL                | :white_check_mark: |
| Datasink (output) | MSSQL                | :white_check_mark: |
| Datasink (output) | Oracle               | :x:                |
| Datasink (output) | PostgreSQL           | :white_check_mark: |
| Datasink (output) | Kafka                | :white_check_mark: |
| Datasink (output) | Azure Event Hub      | :white_check_mark: |
| Datasink (output) | Azure Blob Storage   | :white_check_mark: |
| Datasink (output) | S3                   | :white_check_mark: |
| Datasink (output) | Google Cloud Storage | :x:                |

- :white_check_mark: - Working
- :large_orange_diamond: - Partially supported (alpha)
- :x: - Not supported yet

## Contributing

For details on contributing to this repository, see the [contributing guide](CONTRIBUTING.md).

This project welcomes contributions and suggestions. Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit [https://cla.microsoft.com](https://cla.microsoft.com).

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
