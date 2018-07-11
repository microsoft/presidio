[![Build Status](https://travis-ci.org/presid-io/presidio.svg?branch=development)](https://travis-ci.org/presid-io/presidio)


# Presidio - Data Loss Prevention API
**A context aware, born to the cloud, customizable data loss prevention service**

<p align="center">
<img width="200" alt="logo-presidio" src="https://user-images.githubusercontent.com/17064840/42585165-8fc7b820-853d-11e8-9450-4ce426fb5fe0.png">
</p>

## Description

Presidio *(Origin from Latin praesidium ‘protection, garrison’)* helps to ensure sensitive text is properly managed and governed. It provides fast ***analytics*** and ***anonymization*** for sensitive text such as credit card numbers, bitcoin wallets, names, locations, social security numbers, US phone numbers and financial data. 
Presidio analyzes the text using predefined analyzers to identify patterns, formats, and checksums with relevant context. 

## Features

* Text analytics - Predefined analyzers with customizable fields.
* Probability scores - Customize the sensitive text detection threshold.
* Anonymization - Anonymize sensitive text and images
* Workflow and pipeline integration -  Monitor your data with periodic scans or events of
  1. Storage solutions
      - Azure Blob Storage
      - S3
      - Google Cloud Storage
  2. Databases
      - MySQL
      - PostgreSQL
      - Sql Server
      - Oracle

  and export the results for further analytics:
  1. Databases
  2. Data Warehouse
  3. Streaming platform
      - Kafka
      - Azure Events Hubs
      - Kinesis


## The Technology Stack
Presidio leverages 

* [Kubernetes](https://kubernetes.io/)
* [Consul](https://www.consul.io/)
* [Istio](https://istio.io)
* [spaCy](https://spacy.io/)
* [Redis](https://redis.io/)
* [GRPC](https://grpc.io)


The [design document](/docs/design.md) introduces Presidio concepts and architecture.

## Quickstart

1. Install [Presidio](docs/installation.md)
2. Create a Presidio project
3. Start using the Presidio analyze and anonymize services


**Note:** Examples are made with [HTTPie](https://httpie.org/)

***Sample 1***

1. Create an analyzer project
```
echo -n '{"fields":[]}' | http <api-service-address>/api/v1/templates/<my-project>/analyze/<my-template-name>
```

2. Analyze text
```
echo -n '{"text":"my credit card number is 2970-84746760-9907 345954225667833 4961-2765-5327-5913", "AnalyzeTemplateId":"<my-template-name>"  }' | http <api-service-address>/api/v1/projects/<my-project>/analyze
```

***Sample 2***

1. Create an analyzer project
```
echo -n '{"fields":[{"name":"PHONE_NUMBER"}, {"name":"LOCATION"}, {"name":"DATE_TIME"]}}' | http <api-service-address>/api/v1/templates/<my-project>/analyze/<my-template-name>
```

2. Analyze text
```
echo -n '{"text":""We met yesterday morning in Seattle and his phone number is (212) 555 1234"", "AnalyzeTemplateId":"<my-template-name>"  }' | http <api-service-address>/api/v1/projects/<my-project>/analyze
```

***Sample 3***

1. Create an anonymizer template (This template replaces values in PHONE_NUMBER and redacts CREDIT_CARD)
```
echo -n '{"name":"PHONE_NUMBER","displayName":"Phone number","fieldTypeTransformations":[{"fields":[],"transformation":{"replaceValue":{"newValue":"\u003cphone-number\u003e"}}}]}' | http <api-service-address>/api/v1/templates/<my-project>/anonymize/<my-anonymize-template-name>
```

2. Anonymize text
```
echo -n '{"text":"my phone number is 057-555-2323 and my credit card is 4961-2765-5327-5913", "AnalyzeTemplateId":<my-analyze-template-name>, "AnonymizeTemplateId":<my-anonymize-template-name>  }' | http <api-service-address>/api/v1/projects/<my-project>/anonymize
```

<hr>
<div>Logo made with <a href="https://www.designevo.com/en/" title="Free Online Logo Maker">DesignEvo</a></div>


