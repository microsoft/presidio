# Presidio design

_This is a living document, and is kept up to date with the current state of
presidio. It is a high-level explanation of the presidio design._

## Framework Deployment


## Kubernetes Deployment

![persidium design](https://user-images.githubusercontent.com/17064840/43044585-7246191e-8db1-11e8-8aab-f6ef69265c0e.png)

This architecture gives us the following advantages:
* Resiliency for inter-service communications: Circuit-breaking, retries and timeouts, fault injection, fault handling, load balancing and failover.
* Service Discovery: Discovery of service endpoints through a dedicated service registry.
* Routing: Primitive routing capabilities, but no routing logics related to the business functionality of the service.
* Observability: Metrics, monitoring, distributed logging, distributed tracing.
* Deployment: Native support for containers. Docker and Kubernetes.
