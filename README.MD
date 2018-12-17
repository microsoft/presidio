[![Build status](https://dev.azure.com/csedevil/Presidio/_apis/build/status/Presidio-CI)](https://dev.azure.com/csedevil/Presidio/_build/latest?definitionId=48)


# Presidio - Data Loss Prevention API
**Context aware, born to the cloud, customizable data loss prevention service**

:warning: ***This project is experimental and should not be used for production***

## Description

Presidio *(Origin from Latin praesidium ‘protection, garrison’)* helps to ensure sensitive text is properly managed and governed. It provides fast ***analytics*** and ***anonymization*** for sensitive text such as credit card numbers, bitcoin wallets, names, locations, social security numbers, US phone numbers and financial data. 
Presidio analyzes the text using predefined analyzers to identify patterns, formats, and checksums with relevant context. 

You can find a more detailed list [here](https://microsoft.github.io/presidio/field_types.html)

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
  2. Streaming platform
      - Kafka
      - Azure Events Hubs

## The Technology Stack
Presidio leverages 

* [Kubernetes](https://kubernetes.io/)
* [spaCy](https://spacy.io/)
* [Redis](https://redis.io/)
* [GRPC](https://grpc.io)


The [design document](https://microsoft.github.io/presidio/design.html) introduces Presidio concepts and architecture.

## Quickstart

1. Install [Presidio](https://microsoft.github.io/presidio/install.html)
2. Create a Presidio project
3. Start using the Presidio analyze and anonymize services


**Note:** Examples are made with [HTTPie](https://httpie.org/)

***Sample 1***
1. Analyze text
```
echo -n '{"text":"John Smith lives in New York. We met yesterday morning in Seattle. I called him before on (212) 555-1234 to verify the appointment. He also told me that his drivers license is AC333991", "analyzeTemplate":{"fields":[]}  }' | http <api-service-address>/api/v1/projects/<my-project>/analyze
```

***Sample 2***

You can also create reusable templates 

1. Create an analyzer project
```
echo -n '{"fields":[]}' | http <api-service-address>/api/v1/templates/<my-project>/analyze/<my-template-name>
```

2. Analyze text
```
echo -n '{"text":"my credit card number is 2970-84746760-9907 345954225667833 4961-2765-5327-5913", "AnalyzeTemplateId":"<my-template-name>"  }' | http <api-service-address>/api/v1/projects/<my-project>/analyze
```

***Sample 3***

1. Create an analyzer project
```
echo -n '{"fields":[{"name":"PHONE_NUMBER"}, {"name":"LOCATION"}, {"name":"DATE_TIME"}]}' | http <api-service-address>/api/v1/templates/<my-project>/analyze/<my-template-name>
```

2. Analyze text
```
echo -n '{"text":"We met yesterday morning in Seattle and his phone number is (212) 555 1234", "AnalyzeTemplateId":"<my-template-name>"  }' | http <api-service-address>/api/v1/projects/<my-project>/analyze
```

***Sample 4***

1. Create an anonymizer template (This template replaces values in PHONE_NUMBER and redacts CREDIT_CARD)
```
echo -n '{"fieldTypeTransformations":[{"fields":[{"name":"PHONE_NUMBER"}],"transformation":{"replaceValue":{"newValue":"\u003cphone-number\u003e"}}},{"fields":[{"name":"CREDIT_CARD"}],"transformation":{"redactValue":{}}}]}' | http <api-service-address>/api/v1/templates/<my-project>/anonymize/<my-anonymize-template-name>
```

2. Anonymize text
```
echo -n '{"text":"my phone number is 057-555-2323 and my credit card is 4961-2765-5327-5913", "AnalyzeTemplateId":"<my-analyze-template-name>", "AnonymizeTemplateId":"<my-anonymize-template-name>"  }' | http <api-service-address>/api/v1/projects/<my-project>/anonymize
```


### Current Features Status

| Module              | Feature              | Status                 |
|---------------------|----------------------|------------------------|
| API                 | HTTP input           | :white_check_mark:     |
| Scanner             | MySQL                | :x:                    |
| Scanner             | MSSQL                | :x:                    |
| Scanner             | PostgreSQL           | :x:                    |
| Scanner             | Oracle               | :x:                    |
| Scanner             | Azure Blob Storage   | :white_check_mark:     |
| Scanner             | S3                   | :white_check_mark:     |
| Scanner             | Google Cloud Storage | :x:                    |
| Streams             | Kafka                | :large_orange_diamond: |
| Streams             | Azure Event Hub      | :large_orange_diamond:                    |
| Datasink (output)   | MySQL                | :white_check_mark:     |
| Datasink (output)   | MSSQL                | :white_check_mark:     |
| Datasink (output)   | Oracle               | :x:                    |
| Datasink (output)   | PostgreSQL           | :white_check_mark:     |
| Datasink (output)   | Kafka                | :white_check_mark:     |
| Datasink (output)   | Azure Event Hub      | :white_check_mark:     |
| Datasink (output)   | Azure Blob Storage   | :white_check_mark:     |
| Datasink (output)   | S3                   | :white_check_mark:     |
| Datasink (output)   | Google Cloud Storage | :x:                    |

- :white_check_mark: - Working
- :large_orange_diamond: - Partially working
- :x: - Not working yet but we are on it :wink:

# Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.