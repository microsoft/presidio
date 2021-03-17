# Databricks notebook source
# MAGIC %md
# MAGIC # Anonymize PII Entities in text files
# MAGIC
# MAGIC <br>Using Presidio, anonymize PII content of files in an Azure Storage account.
# MAGIC
# MAGIC <br>The following code sample will:
# MAGIC <ol>
# MAGIC <li>Import the content of text files located in an Azure Storage blob folder</li> # noqa D501
# MAGIC <li>Anonymize the content using Presidio</li>
# MAGIC <li>Write the anonymized content back to the Azure Storage blob account</li>
# MAGIC </ol>

# COMMAND ----------

from azure.storage.blob import BlobServiceClient
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import AnonymizerConfig
from pyspark.sql.types import StringType
from pyspark.sql.functions import input_file_name, regexp_replace
from pyspark.sql.functions import col, pandas_udf
import pandas as pd

dbutils.widgets.text("storage_account_name", "", "Blob Storage Account Name")
dbutils.widgets.text("storage_container_name", "", "Blob Container Name")
dbutils.widgets.text("storage_account_access_key", "", "Storage Account Access Key")
dbutils.widgets.text("storage_input_folder", "input", "Input Folder Name")
dbutils.widgets.text("storage_output_folder", "output", "Output Folder Name")

# COMMAND ----------

# MAGIC %md
# MAGIC # Import the text files from Azure Blob storage

# COMMAND ----------

storage_account_name = dbutils.widgets.get("storage_account_name")
storage_container_name = dbutils.widgets.get("storage_container_name")
storage_account_access_key = dbutils.widgets.get("storage_account_access_key")

# mount the container
spark.conf.set(
    "fs.azure.account.key." + storage_account_name + ".blob.core.windows.net",
    storage_account_access_key,
)

dbutils.fs.mount(
    source="wasbs://"
    + storage_container_name
    + "@"
    + storage_account_name
    + ".blob.core.windows.net",
    mount_point="/mnt/files",
    extra_configs={
        "fs.azure.account.key."
        + storage_account_name
        + ".blob.core.windows.net": storage_account_access_key
    },
)

# load the files
input_df = spark.read.text("/mnt/files/input/*").withColumn(
    "filename", input_file_name()
)
display(input_df)


# COMMAND ----------

# MAGIC %md
# MAGIC # Anonymize Text using Presidio

# COMMAND ----------

# define a pandas UDF function and a series function over it.
# Note that analyzer is loaded within the UDF and not broadcasted.
# This is due to spacy limitation of loading models in multiple threads as
# described here: https://github.com/explosion/spaCy/issues/4349
def anonymize_text(text: str) -> str:
    analyzer = AnalyzerEngine()
    anonymizer = AnonymizerEngine()
    analyzer_results = analyzer.analyze(text=text, language="en")
    anonymized_results = anonymizer.anonymize(
        text=text,
        analyzer_results=analyzer_results,
        anonymizers_config={
            "DEFAULT": AnonymizerConfig("replace", {"new_value": "<ANONYMIZED>"})
        },
    )
    return anonymized_results


def anonymize_series(s: pd.Series) -> pd.Series:
    return s.apply(anonymize_text)


# define a the function as pandas UDF
anonymize = pandas_udf(anonymize_series, returnType=StringType())

# apply the udf
anonymized_df = input_df.withColumn("anonymized_text", anonymize(col("value")))
display(anonymized_df)

# COMMAND ----------

# MAGIC %md
# MAGIC # Write the Anonymized content back to Azure Blob storage

# COMMAND ----------

# define a pandas UDF function and a series function over it.
# Note that this is not using the native write API but the Azure
# client to allow writing each row as a separate blob from worker.


def upload_to_blob(text, file_name):
    blob_client = blob_service_client.get_blob_client(
        container=storage_container_name, blob=file_name
    )
    blob_client.upload_blob(text)
    return "SAVED"


def upload_series(s1: pd.Series, s2: pd.Series) -> pd.Series:
    return pd.Series([upload_to_blob(c1, c2) for c1, c2 in zip(s1, s2)])


# define a the function as pandas UDF
save_udf = pandas_udf(upload_series, returnType=StringType())

# setup a Azure Blob client.
blob_service_client = BlobServiceClient(
    account_url="https://" + storage_account_name + ".blob.core.windows.net/",
    credential=storage_account_access_key,
)

# transform the input file name to output file name
anonymized_df = anonymized_df.withColumn(
    "filename",
    regexp_replace(
        "filename",
        "^.*(/" + dbutils.widgets.get("storage_input_folder") + "/)",
        dbutils.widgets.get("storage_output_folder") + "/",
    ),
)

# apply the udf
out_df = anonymized_df.withColumn(
    "processed", save_udf(col("anonymized_text"), col("filename"))
)

out_df.collect()

# unmount the blob container
dbutils.fs.unmount("/mnt/files")
