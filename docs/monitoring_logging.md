# Presidio logging and monitoring design concepts

Presidio accomodates a number of ways to collect logs, metrics and traces using cloud-native standards enabled by its runtime, kubnernetes.  
The following document describes a number of use-cases suited for different environments and requirements from the logging system which have been tested by the presidio team. 

## Logging and Monitoring Basics

- Logs are text-based records of events that occur while the application is running. 
- Metrics are numerical values that can be analyzed. different types of metrics include:
    - Node-level and Container metrics including CPU, memory, network, disk, and file system usage.
    - Application metrics. This includes any metrics that are relevant to understanding the behavior of a service as well as custom metrics that are specific to the domain
    - Dependent service metrics.
- Distributed Tracing - is used to profile and monitor applications built using a microservices architecture using a correlation ID.

[Read more](https://docs.microsoft.com/en-us/azure/architecture/microservices/logging-monitoring) to learn about implementing logging and monitoring microservices.

### Technology Options

- Azure Kubernetes Engine (AKS) and Azure Monitor logging and metrics 
When deploying presidio to AKS, Azure Monitor provides the easiest way to manage logs and metrics using OOTB tooling.
There are a number of ways to enable Azure Monitor on either a new or an exisint cluster
bla bla using Azure Monitor

- Logging with Elasticsearch, Kibana, FluentD\Fluent-bit
bla bla using EFK

- Metrics and Distributed Tracing (Service Level)
