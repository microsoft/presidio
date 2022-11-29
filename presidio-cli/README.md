# Presidio CLI

[![PyPI license](https://img.shields.io/pypi/l/presidio-cli.svg)](https://pypi.python.org/pypi/presidio-cli/)
[![PyPI version](https://badge.fury.io/py/presidio-cli.svg)](https://badge.fury.io/py/presidio-cli)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)
[![PyPI download month](https://img.shields.io/pypi/dm/presidio-cli.svg)](https://pypi.python.org/pypi/presidio-cli/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/presidio-cli.svg)](https://pypi.python.org/pypi/presidio-cli/)

CLI tool that analyzes text for PII Entities using Presidio Analyzer.

## Prerequisities

`Python` version: 3.8, 3.9, 3.10

`pipenv` app installed:

```shell
# check if app is installed
pipenv --version

# install, if not available
pip install pipenv
```

## Install `presidio-cli` in a virtual env

### Install from Python Package Index

install in current python env

```shell
python -m pip install presidio-cli
```

install required apps and presidio-cli in virtual environment

```shell
pipenv install presidio-cli
```

### Install from source

```shell
# clone from git
git clone https://github.com/microsoft/presidio
cd presidio/presidio-cli
# install required apps and presidio-cli
pipenv install --deploy --dev
```

## Install language models for `spaCy`

Load models for the English (en) language using the command presented below. For further information please visit section [models](https://spacy.io/models/en).

```shell
python -m spacy download en_core_web_lg
```

## Configuration file syntax

The default configuration is taken from the `.presidiocli` file in a current directory.

Configuration file supports the following parameters in a yaml file:

- language - the expected language for PII detection. Default is `en`. For supporting additional languages, see [this documentation](https://microsoft.github.io/presidio/analyzer/languages/)

- entities - list of entities to recognize. Maps to the `entities` field in presidio-analyzer. If empty, returns all [supported entities](https://microsoft.github.io/presidio/supported_entities/) for this input language.

- ignore - list of ignored files/folders/directories based on pattern. It is recommended to ignore `Version Control` files, for example `.git`

- allow - list of tokens that should not be marked as PII.

Note: a file requires at least one parameter to be set.

An example of yaml configuration file content:

```yaml
---
language: en
ignore: |
  .git
  *.cfg
entities:
  - PERSON
  - CREDIT_CARD
  - EMAIL_ADDRESS
allow:
  - "allowed token 1"
  - "allowed token 2"

```

## Run the Presidio CLI

Run the Presidio CLI to execute [Presidio Analyzer](https://microsoft.github.io/presidio/analyzer/)
with specified configuration: language, threshold, entities and ignore pre-configured files/paths.

### Configuration from a file

An example of running script with configuration from a file.

There are two example `.yaml` configuration files in the [`conf`](presidio_cli/conf) directory:

- [default.yaml](presidio_cli/conf/default.yaml) - ignore the `.git` directory
- [limited.yaml](presidio_cli/conf/limited.yaml) - limit list of entities used to only 3 of them, ignore `.git` directory and `.cfg` files.

```shell
# run with default configuration (file `.presidiocli`) in the current directory
presidio .

# run with configuration limited.yaml in the "tests" directory
presidio -c presidio_cli/conf/limited.yaml tests/

# run with configuration limited.yaml in single file only tests/test_analyzer.py
presidio -c presidio_cli/conf/limited.yaml tests/test_analyzer.py
```

### Configuration as a parameter

An example of using configuration as data in parameter:

```shell
# ignore paths .git and *.cfg
presidio -d "ignore: |
  .git
  *.cfg" tests/

# limit list of entities to CREDIT_CARD
presidio-d "entities:
  - CREDIT_CARD" tests/

# equivalent to use -c parameter
presidio -d "$(cat presidio_cli/conf/limited.yaml)" tests/
```

### Formatting output

Output can be formatted using `-f` or `--format` parameter. The default format is `auto`.

Available formats:

- standard - standard output format

```shell
presidio -d "entities:
  - PERSON" -f standard tests/conftest.py
# result
tests/conftest.py
  34:58     0.85     PERSON
  37:33     0.85     PERSON
```

- github - similar to diff function in github

```shell
presidio -d "entities:
  - PERSON" -f github tests/conftest.py
# result
::group::tests/conftest.py
::0.85 file=tests/conftest.py,line=34,col=58::34:58 [PERSON]
::0.85 file=tests/conftest.py,line=37,col=33::37:33 [PERSON]
::endgroup::
```

- colored - standard output format but with colors

- parsable - easy to parse automaticaly

```shell
presidio -d "entities:
  - PERSON" -f parsable tests/conftest.py
# result
{"entity_type": "PERSON", "start": 57, "end": 62, "score": 0.85, "analysis_explanation": null}
{"entity_type": "PERSON", "start": 32, "end": 37, "score": 0.85, "analysis_explanation": null}
```

- auto - default format, switches automatically between those 2 modes:
  - github, if run on github - environment variables `GITHUB_ACTIONS` and `GITHUB_WORKFLOW` are set
  - colored, otherwise

### List of all parameters

Simply run the following to get a list of all available options for the CLI:

```shell
presidio --help
```
