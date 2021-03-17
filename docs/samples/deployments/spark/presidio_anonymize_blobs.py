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

dbutils.widgets.text(
    "storage_account_name", "", "Blob Storage Account Name"
)  # noqa: F821
dbutils.widgets.text("storage_container_name", "", "Blob Container Name")  # noqa: F821
dbutils.widgets.text(
    "storage_account_access_key", "", "Storage Account Access Key"
)  # noqa: F821
dbutils.widgets.text(
    "storage_input_folder", "input", "Storage Account Access Key"
)  # noqa: F821
dbutils.widgets.text(
    "storage_output_folder", "output", "Storage Account Access Key"
)  # noqa: F821


# COMMAND ----------

# MAGIC %md
# MAGIC # Import the text files from Azure Blob storage

# COMMAND ----------

storage_account_name = dbutils.widgets.get("storage_account_name")  # noqa F821
storage_container_name = dbutils.widgets.get("storage_container_name")  # noqa F821
storage_account_access_key = dbutils.widgets.get(
    "storage_account_access_key"
)  # noqa F821


blob_service_client = BlobServiceClient(
    account_url="https://" + storage_account_name + ".blob.core.windows.net/",
    credential=storage_account_access_key,
)
container_client = blob_service_client.get_container_client(storage_container_name)

blob_names = container_client.list_blobs(
    name_starts_with=dbutils.widgets.get("storage_input_folder") + "/"
)
blobs = []
for blob in blob_names:
    blobs.append(
        "wasbs://"
        + storage_container_name
        + "@"
        + storage_account_name
        + ".blob.core.windows.net/"
        + blob.name
    )

spark.conf.set(
    "fs.azure.account.key." + storage_account_name + ".blob.core.windows.net",
    storage_account_access_key,
)

input_df = spark.read.text(blobs).withColumn("filename", input_file_name())
display(input_df)


# COMMAND ----------

# MAGIC %md
# MAGIC # Anonymize Text using Presidio

# COMMAND ----------


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


anonymize = pandas_udf(anonymize_series, returnType=StringType())

anonymized_df = input_df.withColumn("anonymized_text", anonymize(col("value")))
display(anonymized_df)


# COMMAND ----------

# MAGIC %md
# MAGIC # Write the Anonymized content back to Azure Blob storage

# COMMAND ----------

anonymized_df = anonymized_df.withColumn(
    "filename",
    regexp_replace(
        "filename",
        "^.*(/" + dbutils.widgets.get("storage_input_folder") + "/)",
        dbutils.widgets.get("storage_output_folder") + "/",
    ),
)


def upload_to_blob(text, file_name):
    blob_client = blob_service_client.get_blob_client(
        container=storage_container_name, blob=file_name
    )
    blob_client.upload_blob(text)
    return "SAVED"


def upload_series(s1: pd.Series, s2: pd.Series) -> pd.Series:
    res = []
    for index, s1_item in s1.items():
        s2_item = s2[index]
        res.append(upload_to_blob(s1_item, s2_item))
    return pd.Series(res)


save_udf = pandas_udf(upload_series, returnType=StringType())

out_df = anonymized_df.withColumn(
    "processed", save_udf(col("anonymized_text"), col("filename"))
)
out_df.collect()
