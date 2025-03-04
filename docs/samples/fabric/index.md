# Presidio with Fabric

This folder contains guides and samples for running Presidio in Microsoft Fabric notebooks with Spark for scalable PII detection and anonymization.

## Contents

1. [Environment Setup](env_setup.md) - How to set up your Fabric environment with the required dependencies.
2. [Notebook Execution](notebook_execution.md) - Step-by-step instructions for running Presidio in a Fabric notebook.
3. [Presidio and Spark Notebook](./presidio_and_spark.ipynb) - The sample notebook demonstrating PII detection and anonymization using Presidio with Spark.
4. [Sample Data](./fabric_sample_data.csv) - Example CSV data for testing the PII detection and anonymization workflow.

## Overview

Microsoft Fabric provides a unified analytics platform, and these samples demonstrate how to leverage Presidio's PII detection and anonymization capabilities at scale using Fabric's Spark processing. The integration enables data engineers and analysts to:

- Detect PII in large datasets using distributed Spark processing
- Anonymize sensitive information in a scalable manner
- Enhance data privacy compliance for analytics workloads