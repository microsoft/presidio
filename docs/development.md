# Setting Up a Development Environment

## Table of contents

## Getting started

### Cloning the repo

TODO: Describe how to clone, folder structure etc.

### Setting up Pipenv

TODO: Add Pipenv documentation from V1.

## Development guidelines

TODO: add description

### Testing

TODO: add
### Linting

Presidio services are PEP8 compliant and continuously enforced on style guide issues during the build process using `flake8`.

Running flake8 locally, using `pipenv run flake8`, you can check for those issues prior to committing a change.

In addition to the basic `flake8` functionality, Presidio uses the following extensions:

- *pep8-naming*: To check that variable names are PEP8 compliant.
- *flake8-docstrings*: To check that docstrings are compliant.

### Automatically format code and check for code styling

To make the linting process easier, you can use pre-commit hooks to verify and automatically format code upon a git commit, using `black`:

1. [Install pre-commit package manager locally.](https://pre-commit.com/#install)

2. From the project's root, enable pre-commit, installing git hooks in the `.git/` directory by running: `pre-commit install`.

3. Commit non PEP8 compliant code will cause commit failure and automatically format your code using `black`, as well as checking code formatting using `flake8`

    ```sh
   > git commit -m 'autoformat' presidio-analyzer/presidio_analyzer/predefined_recognizers/us_ssn_recognizer.py
   
    black....................................................................Failed
    - hook id: black
    - files were modified by this hook
    
    reformatted presidio-analyzer/presidio_analyzer/predefined_recognizers/us_ssn_recognizer.py
    All done! ✨ 🍰 ✨
    1 file reformatted.
    
    flake8...................................................................Passed

    ```

4. Committing again will finish successfully, with a well-formatted code.
