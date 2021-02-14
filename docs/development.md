# Setting Up a Development Environment

## Table of contents

## Getting started

### Cloning the repo

TODO: Describe how to clone, folder structure etc.

### Setting up Pipenv

TODO: Add Pipenv documentation from V1.

## Development guidelines

TODO: add description

### Local build process

After modifying presidio codebase, you might want to build presidio cluster locally, and run tests to spot regressions. 
 The recommended way of doing so is using docker-compose (bundled with 'Docker Desktop' for Windows and Mac systems, 
 more information can be found [here](https://docs.docker.com/compose/install/)).
 Once installed, to start presidio cluster with all of its services in HTTP mode, run from the project root:
```bash
docker-compose up --build -d
```
> Building for the first time might take some time, mainly on downloading the default spacy models.  

To validate that the services were built and started successfuly, and to see the designated port for each, 
use docker ps:

```bash
➜ docker ps
CONTAINER ID   IMAGE                       COMMAND                  CREATED         STATUS         PORTS                    NAMES
6d5a258d19c2   presidio-anonymizer         "/bin/sh -c 'pipenv …"   6 minutes ago   Up 6 minutes   0.0.0.0:5001->5001/tcp   presidio_presidio-anonymizer_1
9aad2b68f93c   presidio-analyzer           "/bin/sh -c 'pipenv …"   2 days ago      Up 6 minutes   0.0.0.0:5002->5001/tcp   presidio_presidio-analyzer_1
1448dfb3ec2b   presidio-image-anonymizer   "/bin/sh -c 'pipenv …"   2 seconds ago   Up 2 seconds   0.0.0.0:5003->5001/tcp   presidio_presidio-image-anonymizer_1
```
Edit docker-compose.yml configuration file to change the default ports.
 
 Starting part of the cluster, or one service only, can be done by stating its image name as argument for docker-compose. 
 For example for analyzer service:
 ```bash
 docker-compose up --build -d presidio-analyzer
 ```
### Testing

TODO: add


### Build and run end-to-end tests locally 

Building and testing presidio locally, as explained above, can give good assurance on new changes and on regressions 
that might have introduced during development. 
As an easier method to build and automatically run end-to-end tests, is to use the `run.bat` script found in the project root:

On Windows CMD / Powershell:
 ```bash
 .\run.bat
 ```
On Mac / Unix-based OS / WSL:
 ```bash
 chmod +x run.bat
 ./run.bat
 ```

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
