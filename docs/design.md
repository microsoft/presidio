# Presidio design

This is a living document, and is kept up to date with the current state of
presidio. It is a high-level explanation of the presidio design.

## Presidio As a Service - Kubernetes Deployment

![persidio-design](https://user-images.githubusercontent.com/17064840/45154654-f706aa80-b1e0-11e8-9ff6-3567f8892bd4.png)


This architecture gives us the following advantages:
* Resiliency for inter-service communications: Circuit-breaking, retries and timeouts, fault injection, fault handling, load balancing and failover.
* Service Discovery: Discovery of service endpoints through a dedicated service registry.
* Routing: Primitive routing capabilities, but no routing logics related to the business functionality of the service.
* Observability: Metrics, monitoring, distributed logging, distributed tracing.
* Deployment: Native support for containers. Docker and Kubernetes.
