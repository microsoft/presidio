# Deploy presidio services to an Azure App Service

Presidio containers can be hosted on an [Azure App Service](https://docs.microsoft.com/en-us/azure/app-service/).
Azure App Service provides a managed production environment, which supports docker containers and devops optimizations. It is a global scale service with built in security and compliance features that fits multiple cloud workloads. The presidio team uses Azure App Service for both its development environment and the presidio demo website.
Follow the provided script to set up an app service for each of the presidio services (analyzer and anonymizer).

## Basic setup

``` bash
RESOURCE_GROUP=<resource group name>
APP_SERVICE_NAME=<name of app service>
LOCATION=<location>
APP_SERVICE_SKU=<sku>
# TODO: take from MCR in user story #2569
IMAGE_NAME=presidio.azurecr.io/presidio-anonymizer:10207
ACR_USER_NAME=<user name>
ACR_USER_PASSWORD=<password>

# create the resource group
az group create --name $RESOURCE_GROUP
# create the app service plan
az appservice plan create --name $APP_SERVICE_NAME-plan --resource-group $RESOURCE_GROUP  \
--is-linux --location $LOCATION --sku $APP_SERVICE_SKU
# create the web app
az webapp create --name $APP_SERVICE_NAME --plan $APP_SERVICE_NAME-plan \
--resource-group $RESOURCE_GROUP -i $IMAGE_NAME -s $ACR_USER_NAME -w $ACR_USER_PASSWORD
```

## Blocking network access

Use the following script to restrict network access for a specific ip such as your computer, a front-end website or an API management.

``` bash
FRONT_END_IP_RANGE=[front end ip range]
az webapp config access-restriction add --resource-group $RESOURCE_GROUP --name $APP_SERVICE_NAME \
  --rule-name 'Front-end allow rule' --action Allow --ip-address $FRONT_END_IP_RANGE --priority 100
```

Further network isolation, using virtual networks, is possible using an Isolated tier of Azure App Service.

## Configure App Service Logging

### Logging to the App Service File System

``` bash
az webapp log config --name $APP_SERVICE_NAME --resource-group $RESOURCE_GROUP \
--application-logging filesystem --detailed-error-messages true \
--docker-container-logging filesystem --level information
```

### Logging to Log Analytics Workspace

``` bash
LOG_ANALYTICS_WORKSPACE_RESROUCE_GROUP=<resource group of log analytics>
LOG_ANALYTICS_WORKSPACE_NAME=<log analytics name>

# create a log analytics workspace
az monitor log-analytics workspace create --resource-group $LOG_ANALYTICS_WORKSPACE_RESROUCE_GROUP --workspace-name $LOG_ANALYTICS_WORKSPACE_NAME

# query the log analytics workspace id
LOG_ANALYTICS_WORKSPACE_ID=$(az monitor log-analytics workspace show --resource-group $LOG_ANALYTICS_WORKSPACE_RESROUCE_GROUP --workspace-name $LOG_ANALYTICS_WORKSPACE_NAME --query id)
# query the app service id
APP_SERVICE_ID=$(az monitor log-analytics workspace show --resource-group $RESOURCE_GROUP --name $APP_SERVICE_NAME --query id)

# create the diagnostics settings
az monitor diagnostic-settings create --name $APP_SERVICE_NAME-diagnostics --resource /
$APP_SERVICE_ID --logs   '[{"category": "AppServicePlatformLogs","enabled": true}, {"category": "AppServiceConsoleLogs", "enabled": true}]' --metrics '[{"category": "AllMetrics","enabled": true}]' --workspace $LOG_ANALYTICS_WORKSPACE_ID
```

## Using an ARM template

Alternatlively, you can use the provided ARM template which can deploy either both or any of the presidio services.
Note that while Log Analytics integration with Azure App Service is in preview, the ARM template deployment will not create a Log Analytics resource or configure the diagnostics settings from the App Service to a Log Analytics workspace.
To deploy the app services using the provided ARM template, fill in the provided values.json file with the required values and run the following script.

```bash
az deployment group create --resource-group $RESOURCE_GROUP --template-file presidio-services.json --parameters @values.json

```

## Deploy Presidio services to Azure

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fmicrosoft%2Fpresidio%2Ffeature%2Fdeploy-to-azure%2Fdocs%2Fdeployment-samples%2Fpresidio-services.json)
