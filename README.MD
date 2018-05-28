[![Build Status](https://travis-ci.org/presidium-io/presidium.svg?branch=development)](https://travis-ci.org/presidium-io/presidium)


# Presidium - Data loss prevention
**A context aware, blazing fast, customizable data loss prevention service**

## Description

Presidium helps you better understand and manage sensitive data. It provides fast, scalable classification and redaction for sensitive data elements like credit card numbers, names, social security numbers, US and selected international identifier numbers, phone numbers. The service classifies this data using more than X predefined detectors to identify patterns, formats, and checksums with contextual clues. You can optionally redact data as well using techniques like masking, secure hashing, and format-preserving encryption.

## Features

* Flexible classification - Pre-defined detectors with a focus on quality, speed, scale.
* Probability scores - Customize the sensitive data detection threshold to fit your needs and reduce noise.
* Detailed findings - Classification results can be sent directly into data warehouse solutions for detailed analysis or export into other systems.
* Easy workload integration - Efficiently deploy and Presidium with templates, monitor your data with periodic scans and integrate into serverless solutions
* Simple and powerful redaction - Redact, mask, tokenize, and transform text and images to help ensure data privacy.

## The Technology Stack
Presidium leverages 

* [Kubernetes](https://kubernetes.io/)
* [Consul](https://www.consul.io/)
* [Conduit](https://conduit.io/)
* [spaCy](https://spacy.io/)
* [Redis](https://redis.io/)
* [GRPC](https://grpc.io)


The [design document](/docs/design.MD) introduces Presidium concepts and architecture.

## Quickstart

1. Install [Presidium](docs/installation.md)
2. Create a Presidium project
3. Start using the Presidium analyze and anonymize services


***Sample 1***

1. Create an analyzer project
```
echo -n '{"fieldTypes":[]}' | http <api-service-address>/api/v1/templates/<my-project>/analyze/<my-template-name>
```

2. Analyze text
```
echo -n '{"text":"my credit card number is 2970-84746760-9907 345954225667833 4961-2765-5327-5913", "AnalyzeTemplateId":"<my-template-name>"  }' | http <api-service-address>/api/v1/projects/<my-project>/analyze
```

***Sample 2***

1. Create an anonymizer template (This template replaces values in PHONE_NUMBER and redacts CREDIT_CARD)
```
echo -n '{"name":"PHONE_NUMBER","displayName":"Phone number","configuration":{"fieldTypeTransformations":[{"fieldTypes":[{"name":"PHONE_NUMBER"}],"transformation":{"replaceValue":{"newValue":"\u003cphone-number\u003e"}}},{"fieldTypes":[{"name":"CREDIT_CARD"}],"transformation":{"redactValue":{}}}]}}' | http <api-service-address>/api/v1/templates/<my-project>/anonymize/<my-anonymize-template-name>
```

2. Anonymize text
```
echo -n '{"text":"my phone number is 057-555-2323 and my credit card is 4961-2765-5327-5913", "AnalyzeTemplateId":<my-analyze-template-name>, "AnonymizeTemplateId":<my-anonymize-template-name>  }' | http 104.214.226.151/api/v1/projects/<my-project>/anonymize
```

***Load test***

1. Create a project (see previous step)
2. Edit  `post.lua`. Change the template name
3. Run [wrk](https://github.com/wg/wrk)

```
wrk -t2 -c2 -d30s -s post.lua http://<api-service-address>/api/v1/projects/<my-project>/analyze
```


