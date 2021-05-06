# Anonymize PII using Presidio on Spark

You can leverages presidio to perform data anonymization as part of spark notebooks.
The following sample uses [Azure Databricks](https://docs.microsoft.com/en-us/azure/databricks/) and simple text files hosted on [Azure Blob Storage](https://docs.microsoft.com/en-us/azure/storage/blobs/). However, it can easily change to fit any other scenario which requires PII analysis or anonymization as part of spark jobs.

**Note** that this code works for Databricks runtime 8.1 (spark 3.1.1) and the libraries described [here](https://docs.microsoft.com/en-us/azure/databricks/release-notes/runtime/8.1).

## Pre-requisites

Provision and setup the required infrastrucutre

### Deploy Infrastructure

Provision the Azure resources by running the following script.

``` bash
export RESOURCE_GROUP=[resource group name]
export STORAGE_ACCOUNT_NAME=[storage account name]
export STORAGE_CONTAINER_NAME=[blob container name]
export DATABRICKS_WORKSPACE_NAME=[databricks workspace name]
export DATABRICKS_SKU=[basic/standard/premium]
export LOCATION=[location]

# Create the resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Use ARM template to build the resources and get back the workspace URL
deployment_response=$(az deployment group create -g $RESOURCE_GROUP --template-file ./docs/samples/deployments/spark/arm-template/databricks.json  --parameters location=$LOCATION workspaceName=$DATABRICKS_WORKSPACE_NAME storageAccountName=$STORAGE_ACCOUNT_NAME containerName=$STORAGE_CONTAINER_NAME)

DATABRICKS_WORKSPACE_URL=$(echo $deployment_response | jq -r ".properties.outputs.workspaceUrl.value"  )
DATABRICKS_WORKSPACE_ID=$(echo $deployment_response | jq -r ".properties.outputs.workspaceId.value")

```

### Setup Databricks

The following script will setup a new cluster in the databricks workspace and prepare it to run presidio anonymization jobs.
Once finished, the script will output an access key which you can use when working with databricks cli.

``` bash

sh ./scripts/configure_databricks.sh

```

## Running the sample

### Configure the notebook

From Databricks workspace, under notebooks folder, open the provided 01_transform_presidio_text notebook and attach it to the cluster preisidio_cluster.
Run the first code-cell and note the following parameters on the top end of the notebook (notebook widgets) and set them accordingly

* Input Folder - a folder on the container where input files are found.
* Output Folder - a folder on the container where output files will be written to.

### Run the notebook

Upload a text file to the blob storage input folder, using any preferd method ([Azure Portal](https://docs.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-portal), [Azure Storage Explorer](https://docs.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-storage-explorer), [Azure CLI](https://docs.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-cli)).

```bash
az storage blob upload --account-name $STORAGE_ACCOUNT_NAME  --container $STORAGE_CONTAINER_NAME --file ./[file name] --name input/[file name]
```

Run the notebook cells, the output should be csv files which contain two columns, the original file name, and the anonymized content of that file.
