# Databricks notebook source
# MAGIC %md
# MAGIC # Anonymize PII Entities in text files
# MAGIC
# MAGIC <br>Using Presidio, anonymize PII content of files in an Azure Storage account.
# MAGIC
# MAGIC <br>The following code sample will:
# MAGIC <ol>
# MAGIC <li>Import the content of text files located in an Azure Storage blob folder</li>
# MAGIC <li>Anonymize the content using Presidio</li>
# MAGIC <li>Write the anonymized content back to the Azure Storage blob account</li>
# MAGIC </ol>

# COMMAND ----------

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities.engine import OperatorConfig
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
storage_mount_name = "/mnt/files"


# unmount container if previously mounted
def sub_unmount(str_path):
    if any(mount.mountPoint == str_path for mount in dbutils.fs.mounts()):
        dbutils.fs.unmount(str_path)


sub_unmount(storage_mount_name)

# mount the container
dbutils.fs.mount(
    source="wasbs://"
    + storage_container_name
    + "@"
    + storage_account_name
    + ".blob.core.windows.net",
    mount_point=storage_mount_name,
    extra_configs={
        "fs.azure.account.key."
        + storage_account_name
        + ".blob.core.windows.net": storage_account_access_key
    },
)

# load the files
input_df = spark.read.text(
    storage_mount_name + "/" + dbutils.widgets.get("storage_input_folder") + "/*"
).withColumn("filename", input_file_name())
display(input_df)


# COMMAND ----------

# MAGIC %md
# MAGIC # Anonymize Text using Presidio

# COMMAND ----------

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()
broadcasted_analyzer = sc.broadcast(analyzer)
broadcasted_anonymizer = sc.broadcast(anonymizer)

# define a pandas UDF function and a series function over it.
# Note that analyzer and anonymizer are broadcasted.


def anonymize_text(text: str) -> str:
    try:
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
    except Exception as e:
        print(f"An exception occurred. {e}")


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


# remove hdfs prefix from file name
anonymized_df = anonymized_df.withColumn(
    "filename",
    regexp_replace("filename", "^.*(" + storage_mount_name + "/)", ""),
)
anonymized_df = anonymized_df.drop("value")
display(anonymized_df)
anonymized_df.write.csv(
    storage_mount_name + "/" + dbutils.widgets.get("storage_output_folder")
)
