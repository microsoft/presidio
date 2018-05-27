# Presidium design

_This is a living document, and is kept up to date with the current state of
Presidium. It is a high-level explanation of the Presidium design._

![persidium design](https://user-images.githubusercontent.com/17064840/40309169-3b0fac24-5d11-11e8-848d-f1686b7689e9.png)


This architecture gives us the following advantages:
* Resiliency for inter-service communications: Circuit-breaking, retries and timeouts, fault injection, fault handling, load balancing and failover.
* Service Discovery: Discovery of service endpoints through a dedicated service registry.
* Routing: Primitive routing capabilities, but no routing logics related to the business functionality of the service.
* Observability: Metrics, monitoring, distributed logging, distributed tracing.
* Deployment: Native support for containers. Docker and Kubernetes.
