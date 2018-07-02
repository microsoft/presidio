# Presidium

## Kubernetes installation

1. Install [consul](https://hub.kubeapps.com/charts/stable/consul)
```
$ helm install --name consul stable/consul --namespace kube-system
```

2. Install [Redis](https://hub.kubeapps.com/charts/stable/redis)
```
$ helm install --name redis stable/redis --set usePassword=false --namespace presidium
```

* **First time only - Install the Conduit CLI**

```
$ curl https://run.conduit.io/install | sh
```

3. Install Conduit

```
$ conduit install | kubectl apply -f -
```

4. View the dashboard!

```
$ conduit dashboard
```

5. Verify that consul and Redis are installed correctly

6. Inject and Deploy

```
$ kubectl create namespace presidium
$ conduit inject deployment/presidium.yaml | kubectl apply -f - --namespace presidium
<<<<<<< HEAD
```
=======
```
>>>>>>> development
