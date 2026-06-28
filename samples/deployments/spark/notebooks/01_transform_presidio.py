# Databricks notebook source
# MAGIC %md
# MAGIC # Anonymize PII Entities with Presidio
# MAGIC
# MAGIC <br>Using Presidio, anonymize PII content in text or csv files.
# MAGIC
# MAGIC <br>The following code sample:
# MAGIC <ol>
# MAGIC <li>Imports the content of a single csv file, or a collection of text files, from a mounted folder</li>
# MAGIC <li>Anonymizes the content of the text files, or a single column in the csv dataset, using Presidio</li>
# MAGIC <li>Writes the anonymized content back to the mounted folder, as csv set, under the output folder.
# MAGIC   The output set from text files anonymization includes a column with the original file path</li>
# MAGIC </ol>
# MAGIC
# MAGIC <br>Input Parameters (widgets):
# MAGIC <ol>
# MAGIC <li>Input File Format (file_format) - Input file format, can be either csv or text.</li>
# MAGIC <li>Input path (storage_input_path) - Folder name in case of text file, a path to a single file in case of csv.</li>
# MAGIC <li>Output Folder Name (storage_output_folder) - Output folder name</li>
# MAGIC <li>Column to Anonymize (anonymized_column) - Name of column to anonymize in case of csv. NA for text.</li>
# MAGIC </ol>

# COMMAND ----------

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from pyspark.sql.types import StringType
from pyspark.sql.functions import input_file_name, regexp_replace
from pyspark.sql.functions import col, pandas_udf
import pandas as pd
import os

dbutils.widgets.dropdown(
    "file_format", "text", ["text", "csv"], "Input File Format (csv/text)"
)
dbutils.widgets.text("storage_input_path", "input", "Input path (file or folder)")
dbutils.widgets.text("storage_output_folder", "output", "Output Folder Name")
dbutils.widgets.text("anonymized_column", "value", "Column to Anonymize")

# COMMAND ----------

# MAGIC %md
# MAGIC # Import the text files from mounted folder

# COMMAND ----------

storage_mount_name = os.environ["STORAGE_MOUNT_NAME"]
storage_input_path = dbutils.widgets.get("storage_input_path")
storage_output_folder = dbutils.widgets.get("storage_output_folder")
file_format = dbutils.widgets.get("file_format")
anonymized_column = dbutils.widgets.get("anonymized_column")


if file_format == "csv":
    input_df = spark.read.option("header", "true").csv(
        storage_mount_name + "/" + storage_input_path
    )
elif file_format == "text":
    input_df = (
        spark.read.text(storage_mount_name + "/" + storage_input_path + "/*")
        .withColumn("filename", input_file_name())
        .withColumn(
            "filename",
            regexp_replace("filename", "^.*(" + storage_mount_name + "/)", ""),
        )
    )

# load the files
display(input_df)


# COMMAND ----------

# MAGIC %md
# MAGIC # Anonymize text using Presidio

# COMMAND ----------

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()
broadcasted_analyzer = sc.broadcast(analyzer)
broadcasted_anonymizer = sc.broadcast(anonymizer)

# define a pandas UDF function and a series function over it.
# Note that analyzer and anonymizer are broadcasted.


def anonymize_text(text: str) -> str:
    analyzer = broadcasted_analyzer.value
    anonymizer = broadcasted_anonymizer.value
    analyzer_results = analyzer.analyze(text=text, language="en")
    anonymized_results = anonymizer.anonymize(
        text=text,
        analyzer_results=analyzer_results,
        operators={"DEFAULT": OperatorConfig("replace", {"new_value": "<ANONYMIZED>"})},
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
display(anonymized_df)

# COMMAND ----------

# MAGIC %md
# MAGIC # Write the anonymized content back to mounted folder

# COMMAND ----------

# write the dataset to output folder

anonymized_df.write.option("header", "true").csv(
    storage_mount_name + "/" + storage_output_folder
)

# COMMAND ----------
