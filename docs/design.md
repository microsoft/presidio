# Presidio design

This is a living document, and is kept up to date with the current state of
presidio. It is a high-level explanation of the presidio design.

## Presidio As a Service - Kubernetes Deployment

![persidio-design-service](https://user-images.githubusercontent.com/1086572/50959542-e1292f00-14cb-11e9-8847-06e6121ba192.png)


This architecture gives us the following advantages:
* Resiliency for inter-service communications: Circuit-breaking, retries and timeouts, fault injection, fault handling, load balancing and failover.
* Service Discovery: Discovery of service endpoints through a dedicated service registry.
* Routing: Primitive routing capabilities, but no routing logics related to the business functionality of the service.
* Observability: Metrics, monitoring, distributed logging, distributed tracing.
* Deployment: Native support for containers. Docker and Kubernetes.
