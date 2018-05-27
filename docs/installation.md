# Installation

## Kubernetes

1. Install [consul](https://hub.kubeapps.com/charts/stable/consul)
```
$ helm install --name consul stable/consul
```

2. Install [Redis](https://hub.kubeapps.com/charts/stable/redis)
```
$ helm install --name redis stable/redis --set usePassword=false
```

3. Install Presidium
```
helm install --name presidium .
```
