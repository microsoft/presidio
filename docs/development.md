# Setting Up a Development Environment

## Table of contents

1. [Automatically format code and check for code styling](#python-styling)

## Automatically format code and check for code styling <a name='python-styling'></a>

Presidio services are PEP8 compliant and continuously enforced on style guide issues during the build process using `flake8`.

Running flake8 locally, using `pipenv run flake8`, you can check for those issues prior to committing a change.

To make things easier, you can use pre-commit hooks to verify and automatically format code upon a git commit, using `black`:

1. [Install pre-commit package manager locally.](https://pre-commit.com/#install)

1. From the project's root, enable pre-commit, installing git hooks in the `.git/` directory:

    `pre-commit install`

1. Commit non PEP8 compliant code will cause commit failure and automatically format your code using `black`, as well as checking code formatting using `flake8`

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

1. Committing again will finish successfully, with a well-formatted code.
