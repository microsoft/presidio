# Presidio build and release

Presidio continuous processes govern its integrity and stability through the dev, test and and release phases.
The project currently supports [Azure Pipelines](https://azure.microsoft.com/en-us/services/devops/pipelines/) using YAML pipelines which can be easily imported to any Azure Pipelines instance.


## Presidio Azure Devops Pipelines

The following pipelines are provided:

* ***Pull Request pipelines*** - build and test persidio services, or persidio base containers. 

    * [Base images pipeline](../pipelines/PR-deps.yaml)
    * [Presidio image pipeline](../pipelines/PR-presidio.yaml)

* ***Feature Branch pipelines*** - build, test and push to a private container registry, using build-id as the image label. these build either presidio services or the base containers and the depending services.

    * [Base images pipeline](../pipelines/CI-deps-branch.yaml)
    * [Presidio image pipeline](../pipelines/CI-presidio-branch.yaml)

* ***Dev\Master Branch pipelines*** - same process as the feature branch pipelines, but pushing artifacts with both the build-id label and a latest-dev\latest tag (depending on the built branch)

    * [Master Branch Base images pipeline](../pipelines/CI-deps-master.yaml)
    * [Master Branch Presidio image pipeline](../pipelines/CI-presidio-master.yaml)
    * [Development Branch Base images pipeline](../pipelines/CI-deps-dev.yaml)
    * [Development Branch Presidio image pipeline](../pipelines/CI-presidio-dev.yaml)

### Note that the following settings have to be set in Azure Pipelines, for each imported pipeline:

#### Variables
* ***registry*** - a docker registry service endpoint to your private docker registry
* ***registry_name*** - the name of the registry

#### Triggers
* ***Build Completion*** - For pipelines with the the naming convention [pipeline-type]-presidio-[branch-name], add a "Build Completion" CI trigger in Azure Pipelines UI, depending on [pipeline-type]-deps-[branch-name], as setting this in YAML is not yet supported in Azure Piplelines ([Feature Request](https://developercommunity.visualstudio.com/content/problem/293487/build-completion-trigger-not-working-for-yaml-buil.html))


### import a pipeline to Azure Devops

* Sign in to your Azure DevOps organization and navigate to your project.

* In your project, navigate to the Pipelines page. Then choose the action to create a new pipeline.

* Walk through the steps of the wizard by first selecting 'Use the classic editor, and select GitHub as the location of your source code.

* You might be redirected to GitHub to sign in. If so, enter your GitHub credentials.

* When the list of repositories appears, select presidio repository.

* Point Azure Pipelines to the relevant yaml definition you'd like to import. Set the pipeline's name, the required triggers and variables and Select Save and run.

* A new run is started. Wait for the run to finish.