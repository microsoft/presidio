# Contributing to Presidio

:tada: Thanks for taking the time to contribute! :tada:

The following is a set of guidelines for contributing to Presidio.

## What do I need to know before I get started?

### Project Presidio

Presidio is a community project aimed at helping everyone handle their private data and make the world a safer place.
Presidio is both a framework and a system. It's a framework in a sense that you could take code parts from it, extend, customize and plug somewhere. It's also a system you could take as a whole or in parts and deploy locally, on-prem on in the cloud.
When contributing to presidio, it's important to keep this in mind, as some "framework" contributions might not be suitable for a deployment, or vice-versa.

### PR guidelines

Commit message should be clear, explaining the committed changes.

Update CHANGELOG.md:

Under Unreleased section, use the category which is most suitable for your change (changed/removed/deprecated).
Document the change with simple readable text and push it as part of the commit.
Next release, the change will be documented under the new version.

### Build and Release process

The project currently supports [Azure Pipelines](https://azure.microsoft.com/en-us/services/devops/pipelines/) using YAML pipelines which can be easily imported to any Azure Pipelines instance.
For more details follow the [Build and Release documentation](docs/build_release.md).

## Getting started with the code

To get started, refer to the documentation for [setting up a development environment](docs/development.md).

### How to test?

For Python, Presidio leverages `pytest` and `ruff`. See [this tutorial](docs/development.md#testing) on more information on testing presidio modules.

### Adding new recognizers for new PII types

Adding a new recognizer is a great way to improve Presidio. A new capability to detect a new type of PII entity improves Presidio's coverage and makes private data less accessible.

Best practices for developing recognizers [are described here](docs/analyzer/developing_recognizers.md). Please follow these guidelines when proposing new recognizers.

#### Contributing a New Predefined Recognizer

To contribute a new predefined recognizer to Presidio Analyzer:

1. **Choose the correct folder:**
   - If your recognizer is specific to a country or region, add it under `presidio-analyzer/presidio_analyzer/predefined_recognizers/country_specific/<country>/`.
   - For globally applicable recognizers, use `generic/`.
   - For recognizers based on NLP engines, use `nlp_engine_recognizers/`.
   - For standalone NER models, use `ner/`.
   - For third-party integrations, use `third_party/`.


2. **Add your recognizer class** in the appropriate folder.

   - **If your recognizer uses regex patterns:**
     - Make regex patterns as specific as possible to minimize false positives.
     - Document the source or reference for any new regex logic (e.g., link to a standard, documentation, or example dataset) in the code as a comment.

3. **Add your recognizer to the configuration:**
   - Add your recognizer to `presidio-analyzer/presidio_analyzer/conf/default_recognizers.yaml`.
   - For country-specific recognizers, set `enabled: false` by default in the YAML configuration.

3. **Update imports:** Add your recognizer to `presidio-analyzer/presidio_analyzer/predefined_recognizers/__init__.py` so it is available for import and backward compatibility.

4. **Update `__all__`:** Add your recognizer class name to the `__all__` list in the same `__init__.py` file.

5. **Testing:**
   - Ensure all existing tests pass.
   - Add or update tests for your new recognizer.

6. **Documentation:**
   - If your recognizer supports a new entity, consider updating the [supported entities list](docs/supported_entities.md).
   - Follow the [best practices for recognizer development](docs/analyzer/developing_recognizers.md) and [adding recognizers](docs/analyzer/adding_recognizers.md).

### Fixing Bugs and improving the code

Please review the open [issues on Github](https://github.com/microsoft/presidio/issues) for known bugs and feature requests. We sometimes add 'good first issue' labels on those we believe are simpler, and 'advanced' labels on those which require more work or multiple changes across the solution.

### Adding samples

We would love to see more samples demonstrating how to use Presidio in different scenarios. If you have a sample that you think would be useful for others, please consider contributing it. You can find the samples in the [samples folder](docs/samples/).

When contributing a sample, make sure it is self contained (e.g. external dependencies are documented), add it [to the index] (docs/samples/index.md), and to the [mkdocs.yml](mkdocs.yml) file.

## Contacting Us

For any questions, please email <presidio@microsoft.com>.

## Contribution guidelines

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit <https://cla.microsoft.com>.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the Microsoft Open Source Code of Conduct. For more information see the Code of Conduct FAQ or contact <opencode@microsoft.com> with any additional questions or comments.
