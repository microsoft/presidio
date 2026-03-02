# Presidio

[![Build Status](https://github.com/microsoft/presidio/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/microsoft/presidio/actions/workflows/ci.yml)
[![MIT license](https://img.shields.io/badge/license-MIT-brightgreen.svg)](http://opensource.org/licenses/MIT)

**Context aware, pluggable and customizable PII de-identification service for text and images.**

## Overview

`presidio` is a convenience meta-package that references and installs
[presidio-analyzer](https://pypi.org/project/presidio-analyzer/), the PII detection engine from the
[Microsoft Presidio](https://github.com/Microsoft/presidio) project.

> **Note:** This package contains no code of its own. It simply pulls in `presidio-analyzer` as a
> dependency. For the full feature set, documentation, and source code please refer to the
> [presidio-analyzer README](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/README.md).

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

## Acknowledgements

The idea of publishing a top-level `presidio` package that references `presidio-analyzer` was
originally proposed and implemented by the contributors of
[papercloudtech/presidio](https://github.com/papercloudtech/presidio). We thank them for the
initiative and for making Presidio more accessible to the community.

## License

MIT License. See [LICENSE](https://github.com/Microsoft/presidio/blob/main/LICENSE) for details.
