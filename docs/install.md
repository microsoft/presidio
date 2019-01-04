# Install guide

You can install Presidio as a service in [Kubernetes](https://kubernetes.io/) or use it as a framework

## The easy way with Docker

```sh
# Build the images

$ export DOCKER_REGISTRY=presidio
$ export PRESIDIO_LABEL=latest
$ make DOCKER_REGISTRY=${DOCKER_REGISTRY} PRESIDIO_LABEL=${PRESIDIO_LABEL} docker-build-deps
$ make DOCKER_REGISTRY=${DOCKER_REGISTRY} PRESIDIO_LABEL=${PRESIDIO_LABEL} docker-build

# Run the containers

$ docker network create mynetwork
$ docker run --rm --name presidio-analyzer --network mynetwork -d -p 3000:3000 -e GRPC_PORT=3000 ${DOCKER_REGISTRY}/presidio-analyzer:${PRESIDIO_LABEL}
$ docker run --rm --name presidio-anonymizer --network mynetwork -d -p 3001:3001 -e GRPC_PORT=3001 ${DOCKER_REGISTRY}/presidio-anonymizer:${PRESIDIO_LABEL}
$ sleep 30 # Wait for the analyzer model to load
$ docker run --rm --name presidio-api --network mynetwork -d -p 8080:8080 -e WEB_PORT=8080 -e ANALYZER_SVC_ADDRESS=presidio-analyzer:3000 -e ANONYMIZER_SVC_ADDRESS=presidio-anonymizer:3001 ${DOCKER_REGISTRY}/presidio-api:${PRESIDIO_LABEL}
```

---

## Presidio As a Service

### Requirements

- Kubernetes 1.9+ with RBAC enabled.
- Helm

### Installation

1. Install [Helm](https://github.com/kubernetes/helm) with [RBAC](https://github.com/kubernetes/helm/blob/master/docs/rbac.md#tiller-and-role-based-access-control)

2. Install [Redis](https://hub.kubeapps.com/charts/stable/redis) (Cache for storage and database scanners)

    ```sh
    $ helm install --name redis stable/redis --set usePassword=false,rbac.create=true --namespace presidio-system
    ```

3. Optional - Ingress controller for presidio API.
    - [Traefik](https://docs.traefik.io/user-guide/kubernetes/)
    - [NGINX](https://docs.microsoft.com/en-us/azure/aks/ingress-tls)

4. Verify that Redis and Traefik/NGINX are installed correctly

5. Deploy from `/charts/presidio`

    ```sh
    # Based on the DOCKER_REGISTRY and PRESIDIO_LABEL from the previous steps
    $ helm install --name presidio-demo --set registry=${DOCKER_REGISTRY},analyzer.tag=${PRESIDIO_LABEL},anonymizer.tag=${PRESIDIO_LABEL},anonymizerimage.tag=${PRESIDIO_LABEL},ocr.tag=${PRESIDIO_LABEL},scheduler.tag=${PRESIDIO_LABEL},api.tag=${PRESIDIO_LABEL},collector.tag=${PRESIDIO_LABEL},datasink.tag=${PRESIDIO_LABEL} . --namespace presidio
    ```

---

Prev: [Overview](overview.md) `|` Next: [Field Types](field_types.md)