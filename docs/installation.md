# Presidium

## Kubernetes installation

1. Install [consul](https://hub.kubeapps.com/charts/stable/consul)
```
$ helm install --name consul stable/consul --namespace consul
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
```

### Testing

#### Simple

1. Create a project
```
echo -n '{"fieldTypes":[]}' | http <api-service-address>/api/v1/templates/<my-project>/analyze/<my-template-name>
```

2. Analyze text
```
echo -n '{"text":"my credit card number is 2970-84746760-9907 345954225667833 4961-2765-5327-5913", "AnalyzeTemplateId":"<my-template-name>"  }' | http <api-service-address>/api/v1/projects/<my-project>/analyze
```

#### Load test

1. Create a project (see previous step)
2. Edit  `post.lua`. Change the template name
3. Run [wrk](https://github.com/wg/wrk)

```
wrk -t2 -c2 -d30s -s post.lua http://<api-service-address>/api/v1/projects/<my-project>/analyze
```