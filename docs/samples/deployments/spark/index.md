# Anonymize PII using Presidio on Spark

You can leverages presidio to perform data anonymization as part of spark notebooks.

The following sample uses [Azure Databricks](https://docs.microsoft.com/en-us/azure/databricks/) and simple text files hosted on [Azure Blob Storage](https://docs.microsoft.com/en-us/azure/storage/blobs/). However, it can easily change to fit any other scenario which requires PII analysis or anonymization as part of spark jobs.

**Note** that this code works for Databricks runtime 8.1 (spark 3.1.1) and the libraries described [here](https://docs.microsoft.com/en-us/azure/databricks/release-notes/runtime/8.1).

## The basics of working with Presidio in Spark

A typical use case of Presidio in Spark is transforming a text column in a data frame, by anonymizing its content. The following code sample, a part of [transform presidio notebook](./notebooks/01_transform_presidio.py), is the basis of the e2e sample which uses Azure Databricks as the Spark environment.

```python
anonymized_column = "value" # name of column to anonymize
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

# broadcast the engines to the cluster nodes
broadcasted_analyzer = sc.broadcast(analyzer)
broadcasted_anonymizer = sc.broadcast(anonymizer)

# define a pandas UDF function and a series function over it.
def anonymize_text(text: str) -> str:
    analyzer = broadcasted_analyzer.value
    anonymizer = broadcasted_anonymizer.value
    analyzer_results = analyzer.analyze(text=text, language="en")
    anonymized_results = anonymizer.anonymize(
        text=text,
        analyzer_results=analyzer_results,
        operators={
            "DEFAULT": OperatorConfig("replace", {"new_value": "<ANONYMIZED>"})
        },
    )
    return anonymized_results.text


def anonymize_series(s: pd.Series) -> pd.Series:
    return s.apply(anonymize_text)


# define a the function as pandas UDF
anonymize = pandas_udf(anonymize_series, returnType=StringType())

# apply the udf
anonymized_df = input_df.withColumn(
    anonymized_column, anonymize(col(anonymized_column))
)

```

## Pre-requisites

If you do not have an instance of Azure Databricks, follow through with the following steps to provision and setup the required infrastrucutre.

If you do have a Databricks workspace and a cluster you wish to configure to run Presidio, jump over to the [Configure an existing cluster](#Configure-an-existing-cluster) section.

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

export DATABRICKS_WORKSPACE_URL=$(echo $deployment_response | jq -r ".properties.outputs.workspaceUrl.value")
export DATABRICKS_WORKSPACE_ID=$(echo $deployment_response | jq -r ".properties.outputs.workspaceId.value")

```

### Setup Databricks

The following script will setup a new cluster in the databricks workspace and prepare it to run presidio anonymization jobs.
Once finished, the script will output an access key which you can use when working with databricks cli.

``` bash

sh ./scripts/configure_databricks.sh

```

### Configure an existing cluster

Only follow through with the steps in this section if you have an existing databricks workspace and clsuter you wish to configure to run presidio. If you've followed through with the "Deploy Infrastructure" and "Setup Databricks" sections you do not have to run the script in this section.

#### Set up secret scope and secrets for storage account

Add an Azure Storage account key to secret scope.

``` bash
STORAGE_PRIMARY_KEY=[Primary key of storage account]

databricks secrets create-scope --scope storage_scope --initial-manage-principal users
databricks secrets put --scope storage_scope --key storage_account_access_key --string-value "$STORAGE_PRIMARY_KEY"

```

#### Upload or update cluster init scripts

Presidio libraries are loaded to the cluster on init.
Upload the cluster setup script or add its content to the existing cluster's init script.

```bash
databricks fs cp "./setup/startup.sh" "dbfs:/FileStore/dependencies/startup.sh"

```

Setup the cluster to run the [init script](https://docs.microsoft.com/en-us/azure/databricks/clusters/configure#init-scripts).

#### Upload presidio notebooks

```bash
databricks workspace import_dir "./notebooks" "/notebooks" --overwrite

```

#### Update cluster environment

Add the following [environment variables](https://docs.microsoft.com/en-us/azure/databricks/clusters/configure#environment-variables) to your databricks cluster:

```bash
"STORAGE_MOUNT_NAME": "/mnt/files"
"STORAGE_CONTAINER_NAME": [Blob container name]
"STORAGE_ACCOUNT_NAME": [Storage account name]

```

#### Mount the storage container

Run the notebook 00_setup to mount the storage account to databricks.

## Running the sample

### Configure Presidio transformation notebook

From Databricks workspace, under notebooks folder, open the provided 01_transform_presidio notebook and attach it to the cluster preisidio_cluster.
Run the first code-cell and note the following parameters on the top end of the notebook (notebook widgets) and set them accordingly

* Input File Format - text (selected).
* Input path - a folder on the container where input files are found.
* Output Folder - a folder on the container where output files will be written to.
* Column to Anonymize - value (selected).

### Run the notebook

Upload a text file to the blob storage input folder, using any preferd method ([Azure Portal](https://docs.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-portal), [Azure Storage Explorer](https://docs.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-storage-explorer), [Azure CLI](https://docs.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-cli)).

```bash
az storage blob upload --account-name $STORAGE_ACCOUNT_NAME  --container $STORAGE_CONTAINER_NAME --file ./[file name] --name input/[file name]
```

Run the notebook cells, the output should be csv files which contain two columns, the original file name, and the anonymized content of that file.
