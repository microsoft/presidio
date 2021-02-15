# Presidio Analyzer

## Description

The Presidio analyzer is a Python based service for detecting PII entities in text.

During analysis, it runs a set of different *PII Recognizers*,
each one in charge of detecting one or more PII entities using different mechanisms.

Presidio analyzer comes with a set of predefined recognizers,
but can easily be extended with other types of custom recognizers.
Predefined and custom recognizers leverage regex, Named Entity Recognition and other types of logic to detect PII in unstructured text.
  
## Table of contents

- [Installation](#installation)
- [Getting started](#getting-started)
  - [Running in Python](#running-in-python)
  - [Running using Docker](#running-using-docker)
- [Creating PII recognizers](#creating-pii-recognizers)
- [API reference](#api-reference)

## Installation

## Getting started

### Running in Python

### Running using Docker

### Additional languages

See [supporting additional languages and ML models](languages.md).

### Explaining the presidio-analyzer decision process

See [tracking the analyzer decision process](decision_process.md).

## Creating PII recognizers

### How to add a new recognizer

TODO AZDO 2856: copy from analyzer README

### Best practices for developing new recognizers

See [the documentation here](developing_recognizers.md)

## API reference
