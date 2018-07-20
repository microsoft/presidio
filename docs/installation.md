# presidio

## Installation - Kubernetes 1.9+ with RBAC

1. Install [Helm](https://github.com/kubernetes/helm) with [RBAC](https://github.com/kubernetes/helm/blob/master/docs/rbac.md#tiller-and-role-based-access-control)

2. Install [Redis](https://hub.kubeapps.com/charts/stable/redis) (Cache for storage and database scanners)
```
$ helm install --name redis stable/redis --set usePassword=false --namespace presidio-system
```

3. Install [Istio](https://istio.io/docs/setup/kubernetes/quick-start/#download-and-prepare-for-the-installation) (Service Mesh for presidio services)

4. Install [Traefik](https://github.com/kubernetes/charts/tree/master/stable/traefik) (Ingress controller for presidio API)
```
$ helm install --name traefik --set rbac.enabled=true stable/traefik --version 1.33.1 --namespace kube-system
```

5. Verify that Redis Traefik and Istio are installed correctly

6. Create namespace and label it
```
$ kubectl create namespace presidio
$ kubectl label namespace presidio istio-injection=enabled
```

7. Deploy 
```
$ kubectl apply -f /deployment/presidio.yaml --namespace presidio
```
or from `/charts/presidio`
```
$ helm install --name presidio-demo . --namespace presidio
```