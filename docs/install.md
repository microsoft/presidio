# Install guide

You can install Presidio as a service in [Kubernetes](https://kubernetes.io/) or use it as a framework

## Framework

### Analyzer module
#### Requirements
- Python 3.6+

#### Installation

```
$ pip3 install presidio-analyzer
$ pip3 install -U spacy
$ pip3 install https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-2.0.0/en_core_web_lg-2.0.0.tar.gz
```


### Anonymizer module

#### Installation

Download the Presidio Anonymizer latest version from Presidio GitHub releases matching your platform.

---

## Presidio As a Service

#### Requirements 
- Kubernetes 1.9+ with RBAC enabled.
- Helm

#### Installation

1. Install [Helm](https://github.com/kubernetes/helm) with [RBAC](https://github.com/kubernetes/helm/blob/master/docs/rbac.md#tiller-and-role-based-access-control)

2. Install [Redis](https://hub.kubeapps.com/charts/stable/redis) (Cache for storage and database scanners)
```
$ helm install --name redis stable/redis --set usePassword=false,rbac.create=true --namespace presidio-system
```

3. Install [Traefik](https://github.com/kubernetes/charts/tree/master/stable/traefik) (Optional - Ingress controller for presidio API)
```
$ helm install --name traefik --set rbac.enabled=true stable/traefik --version 1.33.1 --namespace kube-system
```

4. Verify that Redis and Traefik are installed correctly

5. Deploy from `/charts/presidio`
```
$ helm install --name presidio-demo . --namespace presidio
```

---

Prev: [Overview](overview.md) `|` Next: [Field Types](field_types.md)