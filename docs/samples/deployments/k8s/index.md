# Deploy presidio to Kubernetes

You can install Presidio locally using [KIND](https://github.com/kubernetes-sigs/kind), as a service in [Kubernetes](https://kubernetes.io/) or [AKS](https://docs.microsoft.com/en-us/azure/aks/intro-kubernetes).

- [Deploy locally using KIND](#deploy-locally-with-kind)
- [Deploy with Kubernetes](#presidio-as-a-service-with-kubernetes)
  - [Prerequisites](#prerequisites)
  - [Step by Step Deployment with customizable parameters](#step-by-step-deployment-with-customizable-parameters)

## Deploy locally with KIND

[KIND (Kubernetes IN Docker)](https://github.com/kubernetes-sigs/kind).

1. Install [Docker](https://docs.docker.com/install/).

2. Clone Presidio.

3. Run the following script, which will use KIND (Kubernetes emulation in Docker)

   ```sh
   cd docs/samples/deployments/k8s/deployment/
   ./run-with-kind.sh
   ```

4. Wait and verify all pods are running:

   ```sh
   kubectl get pod -n presidio
   ```

5. Port forwarding of HTTP requests to the API micro-service will be done automatically. In order to run manual:

   ```sh
   kubectl port-forward <presidio-analyzer-pod-name> 8080:8080 -n presidio
   ```

## Presidio As a Service with Kubernetes

### Prerequisites

1. A Kubernetes 1.18+ cluster with [RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/) enabled. If you are using [AKS](https://docs.microsoft.com/en-us/azure/aks/intro-kubernetes) RBAC is enabled by default.

   !!! note: Note
      Note the pod's resources requirements (CPU and memory) and plan the cluster accordingly.

2. [kubectl](https://kubernetes.io/docs/reference/kubectl/overview/) installed. Verify you can communicate with the cluster by running:

     ```sh
     kubectl version
     ```

3. Local [helm](https://helm.sh/) client.
4. **Optional** - Container Registry - such as [ACR](https://docs.microsoft.com/en-us/azure/container-registry/container-registry-intro). Only needed if you are using your own presidio images and not the default ones from from [Microsoft syndicates container catalog](https://azure.microsoft.com/en-in/blog/microsoft-syndicates-container-catalog/)
5. Recent presidio repo is cloned on your local machine.

### Step by step deployment with customizable parameters

1. Install [Helm](https://github.com/kubernetes/helm) with [RBAC](https://github.com/kubernetes/helm/blob/master/docs/rbac.md#tiller-and-role-based-access-control).

2. Optional - Ingress controller for presidio API, e.g., [NGINX](https://docs.microsoft.com/en-us/azure/aks/ingress-tls).

   > Note: Presidio is not deployed with an ingress controller by default.  
   to change this behavior, deploy the helm chart with `ingress.enabled=true` and specify they type of ingress controller to be used with `ingress.class=nginx` (supported classes are: `nginx`).

3. Deploy from `/docs/samples/deployments/k8s/charts/presidio`

   ```sh
   # Based on the DOCKER_REGISTRY and PRESIDIO_LABEL from the previous steps
   helm install --name demo --set registry=${DOCKER_REGISTRY},tag=${PRESIDIO_LABEL} . --namespace presidio
   ```
