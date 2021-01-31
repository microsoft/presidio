# Setting Up a Development Environment

## Table of contents

1. [Getting started](#getting-started)
   - [Cloning the repo](#cloning-the-repo)
   - [Setting up Pipenv](#setting-up-pipenv)
2. [Development guidelines](#development-guidelines)
   - [Testing](#testing)
   - [Linting](#linting)
   - [Automatically format code and check for code styling](#python-styling)

## Getting started <a name='getting-started'></a>

### Cloning the repo

TODO: Describe how to clone, folder structure etc.

### Setting up Pipenv <a name='setting-up-pipenv'></a>

Presidio uses [Pipenv](https://pipenv.pypa.io/en/latest/) TODO: Add Pipenv documentation from V1.

## Development guidelines <a name='development-guidelines'></a>

TODO: add description

### Testing <a name='testing'></a>

TODO: add

### Linting <a name='linting'></a>

Presidio services are PEP8 compliant and continuously enforced on style guide issues during the build process using `flake8`.

Running flake8 locally, using `pipenv run flake8`, you can check for those issues prior to committing a change.

In addition to the basic `flake8` foncutionality, Presidio uses the following extensions:

- *pep8-naming*: To check that variable names are PEP8 compliant.
- *flake8-docstrings*: To check that docstrings are compliant.

### Automatically format code and check for code styling <a name='python-styling'></a>

To make the linting process easier, you can use pre-commit hooks to verify and automatically format code upon a git commit, using `black`:

1. [Install pre-commit package manager locally.](https://pre-commit.com/#install)

1. From the project's root, enable pre-commit, installing git hooks in the `.git/` directory:

    `pre-commit install`

2. Commit non PEP8 compliant code will cause commit failure and automatically format your code using `black`, as well as checking code formatting using `flake8`

    ```
   > git commit -m 'autoformat' presidio-analyzer/presidio_analyzer/predefined_recognizers/us_ssn_recognizer.py
   
    black....................................................................Failed
    - hook id: black
    - files were modified by this hook
    
    reformatted presidio-analyzer/presidio_analyzer/predefined_recognizers/us_ssn_recognizer.py
    All done! ✨ 🍰 ✨
    1 file reformatted.
    
    flake8...................................................................Passed

    ```

3. Committing again will finish successfully, with a well-formatted code.
