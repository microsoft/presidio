# Presidio

[![Build Status](https://github.com/microsoft/presidio/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/microsoft/presidio/actions/workflows/ci.yml)
[![MIT license](https://img.shields.io/badge/license-MIT-brightgreen.svg)](http://opensource.org/licenses/MIT)

**Context aware, pluggable and customizable PII de-identification service for text and images.**

## Overview

`presidio` is a meta-package that installs [presidio-analyzer](https://pypi.org/project/presidio-analyzer/), the PII detection engine from the [Microsoft Presidio](https://github.com/Microsoft/presidio) project.

## Installation

```bash
pip install presidio
```

This will install `presidio-analyzer` and its dependencies.

## Usage

```python
from presidio_analyzer import AnalyzerEngine

analyzer = AnalyzerEngine()
results = analyzer.analyze(text="My name is John Doe", language="en")
print(results)
```

## Documentation

For full documentation, visit [https://microsoft.github.io/presidio](https://microsoft.github.io/presidio).

## License

MIT License. See [LICENSE](https://github.com/Microsoft/presidio/blob/main/LICENSE) for details.
