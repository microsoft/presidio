# Presidio build and release

Presidio continuous processes govern its integrity and stability through the dev, test and and release phases.
The project currently supports [Azure Pipelines](https://azure.microsoft.com/en-us/services/devops/pipelines/) using YAML pipelines which can be easily imported to any Azure Pipelines instance.

## Presidio Azure Devops Pipelines

Azure Pipelines [templates](https://docs.microsoft.com/en-us/azure/devops/pipelines/process/templates?view=azure-devops) allows for code reuse using [YAML Schema](https://docs.microsoft.com/en-us/azure/devops/pipelines/yaml-schema?view=azure-devops&tabs=schema).

***[Presidio CI Pipeline](../pipelines/CI-presidio.yaml)*** - is the pipeline which is used to parameterize the template with variables.

***[Presidio Build and Publish template](../pipelines/templates/build-test-publish.yaml)*** - is the stages-template which contains the pull request validation, CI build, test and publish logic of presidio. The following stages are implemented:

- *Pull Request*

  - *Security Analysis* - Detect security vulnerabilities in code by running Credscan.

  - *Pull Request* - Runs the Makefile instructions which are provided in the [development](./development.md) guide on a build agent. This does not
  require any service principal or logins which facilitates easier contributions from extneral repos as well as validates the stability of the local environment build instructions provided in the guide.

- *CI*

  - *Setup* - This stage verifies if a dependency container stage is required (based on a set of known files). If one of the triggering files are changed, the python and golang deps containers will be rebuilt in the following stages.

  - *Python* - Build, test and publish python service. If the dependency containers are built in a PR/CI execution, they are labeld with the build id, and used later as base containers when building the python service. this stage tags all containers with the build id. For CI triggered builds the containers are also pushed to a registry.

  - *Golang* - Build, test and publish, in parallel, golang service. If the dependency containers are built in a PR/CI execution, they are labeld with the build id, and used later as base containers when building the golang services. this stage tags all containers with the build id. For CI triggered builds the containers are also pushed to a registry.

  - *Functional Tests* - pull and run presidio services and run functional tests on the presidio api.

  - *Publish Artifacts* - For non PR builds, this stage will pull, tag and push all the generated conatiners. for master branch the containers will be tagged as 'latest'. for other branches the tag will hold the branch name.

### Variables used by the pipeline

* ***AZURE_ARTIFACTS_PYPI_INDEX_URL*** - pypi endpoint used to push the presidio analyzer wheel during CI.
* ***AZURE_ARTIFACTS_FEED_NAME*** - name of Azure Artifact's pypi feed endpoint.
* ***PYPI_SERVICE_CONNECTION*** - service connection with pypi credentials.
* ***PYPI_FEED_NAME*** - name of service connection to pypi's feed endpoint.
* ***REGISTRY*** - service connection to docker registry.
* ***REGISTRY_NAME*** - full name of container registry (i.e. presidio.azurecr.io).

### Import a pipeline to Azure Devops

* Sign in to your Azure DevOps organization and navigate to your project.

* In your project, navigate to the Pipelines page. Then choose the action to create a new pipeline.

* Walk through the steps of the wizard by first selecting 'Use the classic editor, and select GitHub as the location of your source code.

* You might be redirected to GitHub to sign in. If so, enter your GitHub credentials.

* When the list of repositories appears, select presidio repository.

* Point Azure Pipelines to the relevant yaml definition you'd like to import. Set the pipeline's name, the required triggers and variables and Select Save and run.

* A new run is started. Wait for the run to finish.
