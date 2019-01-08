# Presidio - Data Protection API

**Context aware, pluggable and customizable data protection and PII anonymization service for text and images**

## Description

Presidio *(Origin from Latin praesidium ‘protection, garrison’)* helps to ensure sensitive text is properly managed and governed. It provides fast ***analytics*** and ***anonymization*** for sensitive text such as credit card numbers, bitcoin wallets, names, locations, social security numbers, US phone numbers and financial data.
Presidio analyzes the text using predefined analyzers to identify patterns, formats, and checksums with relevant context.

You can find a more detailed list [here](https://microsoft.github.io/presidio/field_types.html)

:warning: ***Presidio can help identify sensitive/PII data in un/structured text. However, because Presidio is using trained ML models, there is no guarantee that Presidio will find all sensitive information. Consequently, additional systems and protections should be employed.***

## Features

***Free text anonymization***

[![Image1](https://user-images.githubusercontent.com/17064840/50557166-2048ca80-0ceb-11e9-9153-d39a3f507d32.png)](https://user-images.githubusercontent.com/17064840/50557166-2048ca80-0ceb-11e9-9153-d39a3f507d32.png)

***Text anonymization in images***

[![Image2](https://user-images.githubusercontent.com/17064840/50557215-bc72d180-0ceb-11e9-8c92-4fbc01bbcb2a.png)](https://user-images.githubusercontent.com/17064840/50557215-bc72d180-0ceb-11e9-8c92-4fbc01bbcb2a.png)

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