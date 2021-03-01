# Build and release process

Presidio leverages Azure DevOps YAML pipelines to validate, build, release and deliver presidio.
The pipelines make use of [templates](https://docs.microsoft.com/en-us/azure/devops/pipelines/process/templates?view=azure-devops)
for code reuse using [YAML Schema](https://docs.microsoft.com/en-us/azure/devops/pipelines/yaml-schema?view=azure-devops&tabs=schema).

## Description

The following pipelines are provided and maintained as part of presidio development process:

-   [PR Validation](https://github.com/microsoft/presidio/blob/main/azure-pipelines.yml) - used to validate pull requests.
    -   Linting
    -   Security and compliance analysis
    -   Unit tests
    -   E2E tests
-   [CI](https://github.com/microsoft/presidio/blob/main/azure-pipelines-ci.yml) - triggered on merge to main branch.
    -   Linting
    -   Security and compliance analysis
    -   Unit tests
    -   E2E tests
    -   deploys the artifacts to an internal dev environment.
-   [Release](https://github.com/microsoft/presidio/blob/main/azure-pipelines.yml) - manually triggered.
    -   releases presidio official artifacts
        -   pypi
        -   Microsoft container registry (and docker hub)
        -   GitHub
    -   updates the official demo environment.

### Variables used by the pipelines

#### CI Pipeline

-   **_ACR_AZURE_SUBSCRIPTION_** - Service connection to Azure subscription where Azure Container Registry is.
-   **_ACR_REGISTRY_NAME_** - Name of Azure Container Registry.
-   **_ANALYZER_DEV_APP_NAME_** - Name of existing App Service for Analyzer (development environment).
-   **_ANONYMIZER_DEV_APP_NAME_** - Name of existing App Service for Anonymizer (development environment).
-   **_IMAGE_REDACTOR_DEV_APP_NAME_** - Name of existing App Service for Image Redactor (development environment).
-   **_DEV_AZURE_SUBSCRIPTION_** - Service connection to Azure subscription where App Services are (development environment).
-   **_DEV_RESOURCE_GROUP_NAME_** - Name of resource group where App Services are (development environment).

#### Release Pipeline

-   **_ACR_AZURE_SUBSCRIPTION_** - Service connection to Azure subscription where Azure Container Registry is.
-   **_ACR_REGISTRY_NAME_** - Name of Azure Container Registry.
-   **_ANALYZER_PROD_APP_NAME_** - Name of existing App Service for Analyzer (production environment).
-   **_ANONYMIZER_PROD_APP_NAME_** - Name of existing App Service for Anonymizer (production environment).
-   **_PROD_AZURE_SUBSCRIPTION_** - Service connection to Azure subscription where App Services are (production environment).
-   **_PROD_RESOURCE_GROUP_NAME_** - Name of resource group where App Services are (production environment).

### Import a pipeline to Azure Devops

-   Sign in to your Azure DevOps organization and navigate to your project.
-   In your project, navigate to the Pipelines page. Then choose the action to create a new pipeline.
-   Walk through the steps of the wizard by first selecting 'Use the classic editor, and select GitHub as the location of your source code.
-   You might be redirected to GitHub to sign in. If so, enter your GitHub credentials.
-   When the list of repositories appears, select presidio repository.
-   Point Azure Pipelines to the relevant yaml definition you'd like to import.
    Set the pipeline's name, the required triggers and variables and Select Save and run.
-   A new run is started. Wait for the run to finish.
