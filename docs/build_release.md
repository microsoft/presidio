# Presidio build and release

Presidio continuous processes govern its integrity and stability through the dev, test and and release phases.
The project currently supports [Azure Pipelines](https://azure.microsoft.com/en-us/services/devops/pipelines/) using YAML pipelines which can be easily imported to any Azure Pipelines instance.

## Presidio Azure Devops Pipelines

Azure Pipelines [templates](https://docs.microsoft.com/en-us/azure/devops/pipelines/process/templates?view=azure-devops) allows for code reuse using [YAML Schema](https://docs.microsoft.com/en-us/azure/devops/pipelines/yaml-schema?view=azure-devops&tabs=schema).

***[Presidio CI Pipeline](../pipelines/CI-presidio.yaml)*** - is the pipeline which is used to buil, test and  publish persidio services images.

***[Presidio Build and Push template](../pipelines/templates/build-test-publish.yaml)*** - is the stages-template which contains the build, test and push logic of presidio. There are four stages for the build:

- *Build dependency containers* - This stage verifies if a dependency container stage is required (based on a set of known files). If one of the triggering files are changed, the python and golang deps containers are rebuilt in parallel using different [pipeline jobs](https://docs.microsoft.com/en-us/azure/devops/pipelines/process/phases?view=azure-devops&tabs=yaml)
    It the dependency containers are built in a PR/CI execution, they are labeld with the build id, and used later as base containers when building the presidio services.

- *Build presidio services* - Build and test all presidio servics. this stage tags all containers with the build id. For nonnon-PR builds the containers are also pushed to a registry.

- *Functional Tests* - pull and run presidio services and run functional tests on the presidio api.

- *Publish Artifacts* - For non PR builds, this stage will pull, tag and push all the generated conatiners. for master branch the containers will be tagged as 'latest'. for other branches the tag will hold the branch name.

### Variables used by the pipeline

* ***PYPI_INDEX_URL*** - pypi artifact used to push the wheel.
* ***REGISTRY*** - service connection to docker registry.
* ***REGISTRY_NAME*** - full name of container registry (i.e. presidio.azurecr.io).
* ***DEPENDENCY_DEFAULT*** - presidio release version.


### import a pipeline to Azure Devops

* Sign in to your Azure DevOps organization and navigate to your project.

* In your project, navigate to the Pipelines page. Then choose the action to create a new pipeline.

* Walk through the steps of the wizard by first selecting 'Use the classic editor, and select GitHub as the location of your source code.

* You might be redirected to GitHub to sign in. If so, enter your GitHub credentials.

* When the list of repositories appears, select presidio repository.

* Point Azure Pipelines to the relevant yaml definition you'd like to import. Set the pipeline's name, the required triggers and variables and Select Save and run.

* A new run is started. Wait for the run to finish.