# Presidio - Data Protection and Anonymization API

**Context aware, pluggable and customizable PII anonymization service for text and images.**

## What is Presidio

Presidio _(Origin from Latin praesidium ‘protection, garrison’)_ helps to ensure sensitive text is properly managed and governed. It provides fast **_identification_** and **_anonymization_** modules for sensitive text such as credit card numbers, names, locations, social security numbers, bitcoin wallets, US phone numbers and financial data.

Presidio includes:

1. Predefined or custom PII recognizers leveraging Named Entity Recognition, regular expressions, formats and checksum with relevant context in multiple languages.
2. Options for connecting to external PII detection models.
3. Multiple usage options, from Python or PySpark pipelines to Kubernetes
4. Customizability in PII identification and anonymization.
5. Module for redacting PII text in images.

:warning: Presidio can help identify sensitive/PII data in un/structured text. However, because Presidio is using trained ML models, there is no guarantee that Presidio will find all sensitive information. Consequently, additional systems and protections should be employed.

## Demo

[Try Presidio with your own data](https://aka.ms/presidio-demo)

## Overview

<p align="center">
  <kbd>  
  <img width="-100" height="-50" src="docs/assets/presidio_gif.gif">
  </kbd>
</p>

## Getting started

## Usage documentation

## Samples

## How to contact us?

If you have a usage question, found a bug or have a suggestion for improvement, please file a [Github issue](https://github.com/microsoft/presidio/issues).
For other matters, please email presidio@microsoft.com

---

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
