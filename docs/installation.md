# presidio

## Installation - Kubernetes 1.9+ with RBAC

1. Install [Helm](https://github.com/kubernetes/helm) with [RBAC](https://github.com/kubernetes/helm/blob/master/docs/rbac.md#tiller-and-role-based-access-control)

2. Install [consul](https://hub.kubeapps.com/charts/stable/consul) (presidio internal database and service discovery)
```
$ helm install --name consul stable/consul --namespace presidio-system
```

3. Install [Redis](https://hub.kubeapps.com/charts/stable/redis) (Cache for storage and database scanners)
```
$ helm install --name redis stable/redis --set usePassword=false --namespace presidio-system
```

4. Install [Istio](https://istio.io/docs/setup/kubernetes/quick-start/#download-and-prepare-for-the-installation) (Service Mesh for presidio services)

5. Install [Traefik](https://github.com/kubernetes/charts/tree/master/stable/traefik) (Ingress controller for presidio API)
```
$ helm install --name traefik --set rbac.enabled=true stable/traefik --version 1.33.1 --namespace kube-system
```

6. Verify that consul, Redis Traefik and Istio are installed correctly

7. Create namespace and label it
```
$ kubectl create namespace presidio
$ kubectl label namespace presidio istio-injection=enabled
```

8. Deploy 
```
$ kubectl apply -f /deployment/presidio.yaml --namespace presidio
```
or from `/charts/presidio`
```
$ helm install --name presidio-demo . --namespace presidio
```