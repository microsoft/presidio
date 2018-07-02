[![Build Status](https://travis-ci.org/presidium-io/presidium.svg?branch=development)](https://travis-ci.org/presidium-io/presidium)


# Presidium - Data loss prevention
**A context aware, blazing fast, customizable data loss prevention service**

<p align="center">
  <img src="https://user-images.githubusercontent.com/17064840/41805986-5a1c396a-76bc-11e8-986f-26dd73485e6c.png">
</p>

## Description

Presidium *(Origin from Latin praesidium ‘protection, garrison’)* helps to ensure sensitive text is properly managed and governed. It provides fast ***analytics*** and ***anonymization*** for sensitive text such as credit card numbers, bitcoin wallets, names, locations, social security numbers, US phone numbers and financial data. 
Presidium analyzes the text using predefined analyzers to identify patterns, formats, and checksums with relevant context. 

## Features

* Text analytics - Predefined analyzers with customizable fields.
* Probability scores - Customize the sensitive text detection threshold.
* Detailed analysis - Analytics results can be sent directly into data warehouse solutions for detailed analysis or export into other systems.
* Workflow integration -  Create templates and monitor your data with periodic scans and integrate with various storage solutions such as Azure Storage, S3 and Google Cloud Storage.
* Anonymization - Anonymize text and images

## The Technology Stack
Presidium leverages 

* [Kubernetes](https://kubernetes.io/)
* [Consul](https://www.consul.io/)
* [Conduit](https://conduit.io/)
* [spaCy](https://spacy.io/)
* [Redis](https://redis.io/)
* [GRPC](https://grpc.io)


The [design document](/docs/design.md) introduces Presidium concepts and architecture.

## Quickstart

1. Install [Presidium](docs/installation.md)
2. Create a Presidium project
3. Start using the Presidium analyze and anonymize services


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
echo -n '{"fields":["PHONE_NUMBER", "LOCATION", "DATE_TIME"]}' | http <api-service-address>/api/v1/templates/<my-project>/analyze/<my-template-name>
```

2. Analyze text
```
echo -n '{"text":""We met yesterday morning in Seattle and his phone number is (212) 555 1234"", "AnalyzeTemplateId":"<my-template-name>"  }' | http <api-service-address>/api/v1/projects/<my-project>/analyze
```

***Sample 3***

1. Create an anonymizer template (This template replaces values in PHONE_NUMBER and redacts CREDIT_CARD)
```
echo -n '{"name":"PHONE_NUMBER","displayName":"Phone number","configuration":{"fieldTypeTransformations":[{"fields":[{"name":"PHONE_NUMBER"}],"transformation":{"replaceValue":{"newValue":"\u003cphone-number\u003e"}}},{"fields":[{"name":"CREDIT_CARD"}],"transformation":{"redactValue":{}}}]}}' | http <api-service-address>/api/v1/templates/<my-project>/anonymize/<my-anonymize-template-name>
```

2. Anonymize text
```
echo -n '{"text":"my phone number is 057-555-2323 and my credit card is 4961-2765-5327-5913", "AnalyzeTemplateId":<my-analyze-template-name>, "AnonymizeTemplateId":<my-anonymize-template-name>  }' | http <api-service-address>/api/v1/projects/<my-project>/anonymize
```

***Load test***

1. Create a project (see previous step)
2. Edit  `post.lua`. Change the template name
3. Run [wrk](https://github.com/wg/wrk)

```
wrk -t2 -c2 -d30s -s post.lua http://<api-service-address>/api/v1/projects/<my-project>/analyze
```


<hr>
<div>Logo made with <a href="https://www.designevo.com/en/" title="Free Online Logo Maker">DesignEvo</a></div>


