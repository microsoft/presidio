# Deploy presidio services to an Azure App Service

Presidio containers can be hosted on an Azure App Service.
Follow the provided script to se up an app service for each of the presidio services (analyzer and anonymizer).

## Basic setup

``` bash
RESOURCE_GROUP=[resource group name]
APP_SERVICE_NAME=[name of app service]
LOCATION=[location]
APP_SERVICE_SKU=[sku]
# TODO: take from MCR in user story #2569
IMAGE_NAME=presidio.azurecr.io/presidio-anonymizer:10207
ACR_USER_NAME=[user name]
ACR_USER_PASSWORD=[password]

# create the resource group
az group create --name $RESOURCE_GROUP
# create the app service plan
az appservice plan create --name $APP_SERVICE_NAME-plan --resource-group $RESOURCE_GROUP --is-linux --location $LOCATION --sku $APP_SERVICE_SKU
# create the web app
az webapp create --name $APP_SERVICE_NAME --plan $APP_SERVICE_NAME-plan --resource-group $RESOURCE_GROUP -i $IMAGE_NAME -s $ACR_USER_NAME -w $ACR_USER_PASSWORD
# configure the exposed port
az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $APP_SERVICE_NAME --settings WEBSITES_PORT=3000
```

## Adding Log Analytics

create and configure LA

## Blocking network access

Use the following script to restrict network access for a specific ip such as your computer, a front-end website and an API management.

``` bash
FRONT_END_IP_RANGE=[front end ip range]
az webapp config access-restriction add --resource-group $RESOURCE_GROUP --name $APP_SERVICE_NAME \
  --rule-name 'Front-end allow rule' --action Allow --ip-address $FRONT_END_IP_RANGE --priority 100

```
