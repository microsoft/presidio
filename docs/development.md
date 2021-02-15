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

We strive to have a full test coverage in Presidio, and expect every pull request to
 include tests. 
 
 In each service directory, a 'test' directory can be found. In it, both unit tests,
  for testing single files or classes, and integration tests, for testing integration
   between the service components, or integration with external packages. 
   
#### Basic conventions

For tests to be consistent and predictable, we use the following basic conventions:

 1. Treat tests as production code. Keep the tests concise and readable, with descriptive namings. 
 2. Assert on one behavior at a time in each test.
 3. Test names should follow a pattern of `test_when_[condition_to_test]_then_[expected_behaviour]`.
 For example: test_when_no_interpretability_requested_then_response_contains_no_analysis.
 4. Use test doubles and mocks when writing unit tests. Make less use of them when writing integration tests.

#### Running tests

Presidio uses the [pytest](http://doc.pytest.org/) framework for testing. 
See the pytest [documentation](https://docs.pytest.org/en/latest/contents.html) for more information.

Running the tests locally can be done in two ways:
1. Using cli, from each service directory, run:
    ```shell
   pipenv run pytest
   ```
2. Using your IDE. See configuration examples for [IDEA PyCharm / IntelliJ](https://www.jetbrains.com/help/pycharm/creating-run-debug-configuration-for-tests.html)
    and [Visual Studio Code](https://code.visualstudio.com/docs/python/testing)

#### End-to-end tests

Since Presidio services can function as HTTP servers, Presidio uses an additional
 End-to-end (e2e) testing layer to test their REST APIs.
This e2e test framework is located under 'e2e-tests' directory.
You can also find test scenarios testing the integration between Presidio services. 
These tests should be annotated with 'integration' pytest marker `@pytest.mark.integration`, while 
tests calling a single servcie api layer should be annotated with 'api' pytest marker `@pytest.mark.api`.
 Running the e2e-tests locally can be done in two ways:
 1. Using cli, from e2e-tests directory, run:
    
    On Windows CMD / Powershell:
    ```shell
    # Create a virtualenv named env (needs to be done only on the first run)
    py -m venv env
    # Activate the virtualenv
    env\Scripts\activate
    # Install e2e-tests requirements using pip
    pip install -r requirements.txt
    # Run pytest
    pytest
     # Deactivate the virtualenv
    deactivate
    ```
    On Mac / Unix-based OS / WSL:
     ```shell
    # Create a virtualenv named env (needs to be done only on the first run)
    python -m venv env
    # Activate the virtualenv
    source env/bin/activate
    # Install e2e-tests requirements using pip
    pip install -r requirements.txt
    # Run pytest
    pytest
     # Deactivate the virtualenv
    deactivate
    ```
 2. Using your IDE, see references in the section above.
  
> Note: The e2e tests require a Presidio cluster to be up, for example using the 
containerized cluster with docker-compose.

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
