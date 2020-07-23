# Contributing to Presidio

:tada: Thanks for taking the time to contribute! :tada:

The following is a set of guidelines for contributing to Presidio.

## What do I need to know before I get started?

### Project Presidio

Presidio is a community project aimed at helping everyone handle their private data and make the world a safer place.
Presidio is both a framework and a system. It's a framework in a sense that you could take code parts from it, extend, customize and plug somewhere. It's also a system you could take as a whole or in parts and deploy locally, on-prem on in the cloud, especially when leveraging Kubernetes.
When contributing to presidio, it's important to keep this in mind, as some "framework" contributions might not be suitable for a deployment, or vice-versa.

### Build and Release process

The project currently supports [Azure Pipelines](https://azure.microsoft.com/en-us/services/devops/pipelines/) using YAML pipelines which can be easily imported to any Azure Pipelines instance.
For more details follow the [Build and Release documentation](docs/build_release.md).

## Getting started with the code

To get started, refer to the documentation for [setting up a development environment](docs/development.md).

### General contribution guidelines

- A Github issue suggesting the change should be opened prior to a PR.
- All contributions should be documented, tested and linted. Please verify that all tests and lint checks pass successfully before proposing a change.
- In order for a pull request to be accepted, the CI (containing unit tests, functional tests and linting) needs to succeed, in addition to approvals from two maintainers.
- PRs should be small and solve/improve one issue at a time. If you have multiple suggestions for improvement, please open multiple PRs.


### How can I contribute?

- [Testing](#how-to-test)
- [Adding new recognizers for new PII types](#adding-new-recognizers-for-new-pii-types)
- [Adding new connectors](#adding-new-connectors)
- [Bug fixing and general improvement](#bug-fixing-and-general-improvement)


### How to test?

- For Go, the official methods for testing are used. see https://golang.org/pkg/testing/
- For Python, Presidio leverages `pytest`, `pylint` and `flake8`. See [this tutorial](docs/development.md#dev-python) on more information on testing the presidio-analyzer module.

### Adding new recognizers for new PII types

Adding a new recognizer is a great way to improve Presidio. A new capability to detect a new type of PII entity improves Presidio's coverage and makes private data less accessible.

Best practices for recognizers development [are described here](docs/developing_recognizers.md). Please follow these guidelines when proposing new recognizers.

### Adding new connectors

Presidio's strength lies in its ability to be completely pluggable and customizable. Adding new types of databases, stream-analytics engines and data stores is extremely useful for many users.
Use the following [developer guide](docs/tutorial_connector.md) for adding new connectors.

### Bug fixing and general improvement

Please review the open [issues on Github](https://github.com/microsoft/presidio/issues) for known bugs and feature requests. We sometimes add 'good first issue' labels on those we believe are simpler, and 'advanced' labels on those which require more work or multiple changes across the solution.
