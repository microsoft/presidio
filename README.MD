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



