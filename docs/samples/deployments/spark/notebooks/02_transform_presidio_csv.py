# Databricks notebook source
# MAGIC %md
# MAGIC # Anonymize PII Entities in text files
# MAGIC
# MAGIC <br>Using Presidio, anonymize PII content of files in an Azure Storage account.
# MAGIC
# MAGIC <br>The following code sample will:
# MAGIC <ol>
# MAGIC <li>Import the content of a CSV file located in an Azure Storage blob folder</li>
# MAGIC <li>Anonymize the requested column using Presidio</li>
# MAGIC <li>Write the anonymized content back to the Azure Storage blob account</li>
# MAGIC </ol>

# COMMAND ----------

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities.engine import OperatorConfig
from pyspark.sql.types import StringType
from pyspark.sql.functions import col, pandas_udf
import pandas as pd
import os

dbutils.widgets.text("input_file_path", "input", "Input file path")
dbutils.widgets.text("storage_output_folder", "output", "Output Folder Name")
dbutils.widgets.text("anonymized_column", "output", "Column to Anonymize")

# COMMAND ----------

anonymized_column = dbutils.widgets.get("anonymized_column")
storage_output_folder = dbutils.widgets.get("storage_output_folder")
input_file_path = dbutils.widgets.get("input_file_path")
storage_mount_name = os.environ["STORAGE_MOUNT_NAME"]

# COMMAND ----------

# MAGIC %md
# MAGIC # Import the CSV file from Azure Blob storage

# COMMAND ----------

# load the files
input_df = spark.read.option("header", "true").csv(
    storage_mount_name + "/" + input_file_path
)
display(input_df)

# COMMAND ----------

# MAGIC %md
# MAGIC # Anonymize text in column  using Presidio

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
anonymized_df = input_df.withColumn(
    anonymized_column, anonymize(col(anonymized_column))
)
display(anonymized_df)

# COMMAND ----------

# MAGIC %md
# MAGIC # Write the Anonymized content back to Azure Blob storage

# COMMAND ----------

# Write the anonymized df to the output folder in the Azure container

anonymized_df.write.option("header", "true").csv(
    storage_mount_name + "/" + storage_output_folder
)
