# Presidio logging and monitoring design concepts

Presidio accommodates several ways to collect logs, metrics, and traces using cloud-native standards enabled by its runtime, kubnernetes.  
The following document describes some use-cases suited for different environments and requirements from the logging system which have been tested by the presidio team. 

## Logging and Monitoring Basics

- ***Logs*** are text-based records of events that occur while the application is running. 
- ***Metrics*** are numerical values that can be analyzed. Different types of metrics include:
    - **Node-level and Container metrics** including CPU, memory, network, disk, and file system usage.
    - **Application metrics** include any metrics that are relevant to understanding the behavior of a service as well as custom metrics that are specific to the domain
    - **Dependent service metrics** include external services or endpoints statistics for latency and error rate.
- ***Distributed Tracing*** - is used to profile and monitor applications built using a microservices architecture using a correlation ID.

Visit the [Architecture center](https://docs.microsoft.com/en-us/azure/architecture/microservices/logging-monitoring) to learn about implementing logging and monitoring in microservices.

## Technology Options

The following section covers three logging technology stacks that include potential scenarios in public and private clouds:  
- Azure Monitor
- EFK (Elastic, FluentD, Kibana)
- Kubernetes service mesh (Istio and Linkerd) 

### Azure Kubernetes Engine (AKS) and Azure Monitor logging and metrics 
When deploying presidio to AKS, [Azure Monitor](https://docs.microsoft.com/en-us/azure/azure-monitor/overview) provides the easiest way to manage and query logs and metrics using OOTB tooling.  
There are a number of ways to enable Azure Monitor on either a new or an exising cluster using the portal, CLI and Terraform, [read more](https://docs.microsoft.com/en-us/azure/azure-monitor/insights/container-insights-onboard).

##### Enabling Azure Monitor on AKS using the CLI


```sh
az aks enable-addons -a monitoring -n MyExistingManagedCluster -g MyExistingManagedClusterRG
```

##### Example - Viewing Analyzer Logs

Run the following KQL query in Azure Logs:

```sql
let startTimestamp = ago(1d);
let ContainerIDs = KubePodInventory
| where TimeGenerated > startTimestamp
| where ClusterId =~ "[YOUR_CLUSTER_ID]"
| distinct ContainerID;
ContainerLog
| where ContainerID in (ContainerIDs) and Image contains "analyzer" 
| project LogEntrySource, LogEntry, TimeGenerated, Computer, Image, Name, ContainerID
| order by TimeGenerated desc
| limit 200
```

### Logging with Elasticsearch, Kibana, FluentD

Logs in presidio are outputted to stdrr and stdout as a standard of logging in 12 factor/microservices applications.  
to store logs for long term retention and exploration during failures and RCA, use [elasticsearch](https://github.com/elastic/elasticsearch) or other document databases that are optimized to act as a search engine (solr, splunk, etc). elasticsearch logs are easily queried and visualized using [kibana](https://github.com/elastic/kibana) or [grafana](https://github.com/grafana/grafana).  
Shipping logs from a microservices platform such as kubernetes to the logs database is done using a logs processor\forwarder such as the CNCF project [FluentD](https://www.fluentd.org/).  

##### Enabling EFK on AKS

The following section describes deploying an EFK (Elastic, FluentD, Kibana) stack to a development AKS cluster.  
**Note that:** the following scripts do **not** fit a production environment in terms of security and scale.

- Install elastic 

```sh
helm install stable/elasticsearch --name=elasticsearch --namespace logging --set client.replicas=1 --set master.replicas=1  --set cluster.env.MINIMUM_MASTER_NODES=1 --set cluster.env.RECOVER_AFTER_MASTER_NODES=1 --set cluster.env.EXPECTED_MASTER_NODES=1  --set data.replicas=1 --set data.heapSize=300m  --set master.persistence.storageClass=managed-premium --set data.persistence.storageClass=managed-premium
```

- Install fluent-bit (a lightweight fluentD log-forwarder)

```sh
helm install stable/fluent-bit --name=fluent-bit --namespace=logging --set backend.type=es --set backend.es.host=elasticsearch-client
```

- Install kibana

```sh
helm install stable/kibana --version 3.0.0  --name=kibana --namespace=logging  --set env.ELASTICSEARCH_URL=http://elasticsearch-client:9200 --set files."kibana\.yml"."elasticsearch\.hosts"=http://elasticsearch-client:9200 --set service.type=NodePort --set service.nodePort=31000
```

##### Example - Viewing Analyzer Logs

- Open the kinana dashbaord

```sh
kubectl -n logging port-forward $(kubectl -n logging get pod -l app=kibana -o jsonpath='{.items[0].metadata.name}') 5601:5601
```

- Open your browser at http://localhost:5601

- TODO: continue when we have the logs

### Service Level Metrics and Distributed Tracing

Metrics and tracing provided by kubernetes and by the applications deployed in the cluster are best suited to be exported to a time-series database such as CNCF Prometheus, shipping of metrics and traces to the database is done using a log forwarder such as FluentD.  
When using a service mesh such as istio or linkerd, cluster and service level telemetry are shipped to the database by the mesh using the sidecar containers, and adding distributed correlation-ID to identify the flow of events across services.  

### Using Istio

##### Enabling Istio on AKS

To enable istio on AKS, refer to the [aks documentation](https://docs.microsoft.com/en-us/azure/aks/istio-install).  
To enable istio on your kubernetes cluster, refer to the official [quick-start guide](https://istio.io/docs/setup/kubernetes/install/kubernetes/) or your specific kubernetes hosting solution guide.

##### Example - Presidio Service Metrics

- Open the grafana dashbaord

    ```sh
    kubectl -n istio-system port-forward $(kubectl -n istio-system get pod -l app=grafana -o jsonpath='{.items[0].metadata.name}') 3000:3000
    ```

- Open your browser at http://localhost:3000

- TODO: continue when we have the logs

- Alternatively, open Prometheus dashabord to query the database directly

```sh
kubectl -n istio-system port-forward $(kubectl -n istio-system get pod -l app=prometheus -o jsonpath='{.items[0].metadata.name}') 9090:9090
```

- Open your browser at http://localhost:9090

- TODO: continue when we have the logs

##### Example - Presidio Service Dependecies

- Open the [Kiali](https://www.kiali.io/) service mesh observability dashbaord

```sh
kubectl port-forward -n istio-system $(kubectl get pod -n istio-system -l app=kiali -o jsonpath='{.items[0].metadata.name}') 20001:20001
```

- Open your browser at http://localhost:20001/kiali/console/

- TODO: continue when we have the logs


##### Example - Presidio Distributed Metrics

- Open the [Jaeger](https://www.jaegertracing.io/) service mesh observability dashbaord

```sh
kubectl port-forward -n istio-system $(kubectl get pod -n istio-system -l app=jaeger -o jsonpath='{.items[0].metadata.name}') 16686:16686
```

- Open your browser at http://localhost:16686

- TODO: continue when we have the logs

### Using Linkerd

##### Enabling Linkerd on AKS

To enable linkerd on your kubernetes cluster, refer to the official [quick-start guide](https://linkerd.io/2/getting-started/) or your specific kubernetes hosting solution guide.

##### Example - Presidio Service Mesh Dashbaord and Metrics 

- Open the linkerd dashbaord

```sh
linkerd dashboard
```

- The browser is opened

- TODO: continue when we have the logs
