# Presidio analyzer - Pipenv installation
[Pipenv](https://pipenv.readthedocs.io/en/latest/) is a Python workflow manager, handling dependencies and environment for python packages. This tutorial describes how to install presidio-analyzer locally for development purposes.
### 1. Install pipenv
#### Using Pip:
```
$ pip install --user pipenv
```
#### Homebrew
```
$ brew install pipenv
```

Additional installation instructions: https://pipenv.readthedocs.io/en/latest/install/#installing-pipenv


### 2. Create virtualenv for the project
From the python project's root folder, run:
```
$ pipenv shell
```

### 3. Install all requirements in the Pipfile, including dev requirements

```
$ pipenv install --dev --sequential
```

### 4. Run all tests
```
$ pipenv run pytest
```

### 5. To run arbitrary scripts within the virtual env, start the command with `pipenv run`. For example:
1. `pipenv run flake8 analyzer --exclude "*pb2*.py"`
2. `pipenv run pylint analyzer`
3. `pipenv run pip freeze`

## General pipenv instructions
Pipenv documentation: https://pipenv.readthedocs.io/en/latest/

Useful Pipenv commands:
```
$ pipenv -h
```

General flow for adding a new dependency:
1. Manually add dependency name to Pipfile.
2. Create a new Pipfile.lock and update environment:
```
$ pipenv update --sequential
```

    `pipenv update` runs the `lock` command as well as the `sync` command which installs all requirements in the lock file into the current virtual environment. `--sequential` installs the dependencies sequentially to increase reproducibility.