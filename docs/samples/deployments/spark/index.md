# Anonymize PII using Presidio on Spark

You can leverages presidio to perform data anonymization as part of spark notebooks.
The following sample uses [Azure Databricks](https://docs.microsoft.com/en-us/azure/databricks/) and simple text files hosted on [Azure Blob Storage](https://docs.microsoft.com/en-us/azure/storage/blobs/). However, it can easily change to fit any other scenario which requires PII analysis or anonymization as part of spark jobs.

## Pre-requisites

Provision and setup the required infrastrucutre

### Azure Storage

Provision an Azure storage account using the following script.

``` bash
RESOURCE_GROUP=[resource group name]
STORAGE_ACCOUNT_NAME=[storage account name]
STORAGE_CONTAINER_NAME=[blob container name]
DATABRICKS_WORKSPACE_NAME=[databricks workspace name]
DATABRICKS_SKU=[basic/standard/premium]
LOCATION=[location]

# Create the storage account
az group create --name $RESOURCE_GROUP --location $LOCATION
az storage account create --name $STORAGE_ACCOUNT_NAME --resource-group
$RESOURCE_GROUP

# Get the storage account access key
STORAGE_ACCESS_KEY=$(az storage account keys list --account-name $STORAGE_ACCOUNT_NAME --resource-group $RESOURCE_GROUP --query '[0].value' -o tsv)

# Create a blob container
az storage container create -n $STORAGE_CONTAINER_NAME --account-name $STORAGE_ACCOUNT_NAME
```

### Azure Databricks

Provision an Azure databricks service using the following script.

```bash
az extension add --name databricks

az databricks workspace create --resource-group $RESOURCE_GROUP  --name $DATABRICKS_WORKSPACE_NAME --sku $DATABRICKS_SKU
```

Initialze a cluster, either using the [Azure databricks UI](https://docs.microsoft.com/en-us/azure/databricks/clusters/create) or by following up the next script using [databricks cli](https://docs.microsoft.com/en-us/azure/databricks/clusters/create).

```bash
# Configure databricks token. for host name use https://[databricks region name].azuredatabricks.net. for token acquire a PAT using the following guide: https://docs.microsoft.com/en-us/azure/databricks/dev-tools/api/latest/authentication#--generate-a-personal-access-token
# 
databricks configure --token

databricks clusters create --json "{ 
    \"cluster_name\": \"presidio\",
    \"spark_version\": \"7.5.x-scala2.12\", 
    \"autoscale\": {
        \"min_workers\": 2,
        \"max_workers\": 8
    },
    \"azure_attributes\": { 
        \"first_on_demand\": 1, 
        \"availability\": \"ON_DEMAND_AZURE\", 
        \"spot_bid_max_price\": -1 
    }, 
    \"node_type_id\": \"Standard_F4s_v2\", 
    \"driver_node_type_id\": \"Standard_F4s_v2\", 
    \"spark_env_vars\": { 
        \"PYSPARK_PYTHON\": \"/databricks/python3/bin/python3\" 
    }, 
    \"autotermination_minutes\": 120, 
    \"enable_elastic_disk\": true, 
    \"cluster_source\": \"UI\"
}"

# Note the cluster ID.
```

Configure the cluster by uploading the provided startup script and setting it as part of the cluster initialization process. this stage will load the required Presidio and Azure Storage libraries to the cluster. You can follow through the next script to perform this stage using the databricks cli, or using the [databricks UI](https://docs.microsoft.com/en-us/azure/databricks/clusters/init-scripts#--configure-a-cluster-scoped-init-script).

```bash
# Upload the init script to the file system
databricks fs cp ./startup.sh dbfs:/FileStore/dependencies/startup.sh

# set the cluster init script
databricks clusters edit --json "{
    \"cluster_name\": \"presidio\",
    \"spark_version\": \"7.5.x-scala2.12\", 
    \"autoscale\": {
        \"min_workers\": 2,
        \"max_workers\": 8
    },
    \"azure_attributes\": { 
        \"first_on_demand\": 1, 
        \"availability\": \"ON_DEMAND_AZURE\", 
        \"spot_bid_max_price\": -1 
    }, 
    \"node_type_id\": \"Standard_F4s_v2\", 
    \"driver_node_type_id\": \"Standard_F4s_v2\", 
    \"spark_env_vars\": { 
        \"PYSPARK_PYTHON\": \"/databricks/python3/bin/python3\" 
    }, 
    \"autotermination_minutes\": 120, 
    \"enable_elastic_disk\": true, 
    \"cluster_source\": \"UI\",
    \"init_scripts\": [
        {
            \"dbfs\": {
                \"destination\": \"dbfs:/FileStore/dependencies/startup.sh\"
            }
        }
    ],
    \"cluster_id\": \"[your cluster id]\"
}"
```

## Running the sample

### Import notebook to databricks

Upload the provided notebook, either by using the [databricks UI](https://docs.microsoft.com/en-us/azure/databricks/notebooks/notebooks-manage#--import-a-notebook) or by following up the next script using databricks cli.

```bash
# upload the notebook to a shared folder in the workspace
databricks workspace import_dir . /Shared/presidio/

```

### Configure the notebook

Open the notebook from the location where it was stored in the previous step and attach it to the configured cluster.
Run the first code-cell and note the following parameters on the top end of the notebook (notebook widgets) and set them accordingly

* Blob Storage Account Name - Name of the storage account ($STORAGE_ACCOUNT_NAME)
* Blob Container Name - Name of the blob container ($STORAGE_CONTAINER_NAME)
* Storage Account Access Key - Storage account access key ($STORAGE_ACCESS_KEY)

Additionaly, the following parameters have a default value, which you can change.

* Input Folder - a folder on the container where input files are found.
* Output Folder - a folder on the container where output files will be written to.

### Run the notebook

Upload a file to the blob storage input folder, using any preferd method ([Azure Portal](https://docs.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-portal), [Azure Storage Explorer](https://docs.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-storage-explorer), [Azure CLI](https://docs.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-cli)).

```bash
az storage blob upload --account-name $STORAGE_ACCOUNT_NAME  --container $STORAGE_CONTAINER_NAME --file ./[file name] --name input/[file name]
```

Run the notebook cells and look for the output file at the output folder.