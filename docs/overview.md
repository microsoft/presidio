# Presidio overview

Presidio *(Origin from Latin praesidium ‘protection, garrison’)* helps to ensure sensitive text is properly managed and governed. It provides fast ***analytics*** and ***anonymization*** for sensitive text such as credit card numbers, bitcoin wallets, names, locations, social security numbers, US phone numbers and financial data.
Presidio analyzes the text using predefined analyzers to identify patterns, formats, and checksums with relevant context.

You can find a more detailed list [here](https://microsoft.github.io/presidio/field_types.html)

:warning: ***Presidio can help identify sensitive/PII data in un/structured text. However, because Presidio is using trained ML models, there is no guarantee that Presidio will find all sensitive information. Consequently, additional systems and protections should be employed.***

## Features

* Text analytics - Predefined analyzers with customizable fields.
* Probability scores - Customize the sensitive text detection threshold.
* Anonymization - Anonymize sensitive text and images
* Workflow and pipeline integration -  Monitor your data with periodic scans or events of/from:
  1. Storage solutions
      * Azure Blob Storage
      * S3
      * Google Cloud Storage
  2. Databases
      * MySQL
      * PostgreSQL
      * Sql Server
      * Oracle
  3. Streaming platforms
      * Kafka
      * Azure Events Hubs

  and export the results for further analytics:
  1. Storage solutions
  2. Databases
  3. Streaming platforms

---

Prev: [Docs Index](index.md) `|` Next: [Install Guide](install.md)