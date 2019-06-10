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

### Azure Kubernetes Service (AKS) and Azure Monitor logging and metrics 
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

Logs in presidio are outputted to stderr and stdout as a standard of logging in 12 factor/microservices applications.  
to store logs for long term retention and exploration during failures and RCA, use [elasticsearch](https://github.com/elastic/elasticsearch) or other document databases that are optimized to act as a search engine (solr, splunk, etc). elasticsearch logs are easily queried and visualized using [kibana](https://github.com/elastic/kibana) or [grafana](https://github.com/grafana/grafana).  
Shipping logs from a microservices platform such as kubernetes to the logs database is done using a logs processor\forwarder such as the CNCF project [FluentD](https://www.fluentd.org/).  

##### Enabling EFK on AKS

The following section describes deploying an EFK (Elastic, FluentD, Kibana) stack to a development AKS cluster.  
**Note that:** the following scripts do **not** fit a production environment in terms of security and scale.

- Install elasticsearch

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

- After initilization of kibana index, switch to the "Discover" tab and search for presidio specific logs.

- Search for 'presidio-analyzer' to view logs generated by the analyzer and different recognizers.

### Service Level Metrics and Distributed Tracing

Metrics and tracing provided by kubernetes and by the applications deployed in the cluster are best suited to be exported to a time-series database such as CNCF Prometheus, shipping of metrics and traces to the database is done using a log forwarder such as FluentD.  
When using a service mesh such as istio or linkerd, cluster and service level telemetry are shipped to the database by the mesh using the sidecar containers, and adding distributed correlation-ID to identify the flow of events across services.  

### Using Istio

##### Enabling Istio on AKS

To enable istio on AKS, refer to the [aks documentation](https://docs.microsoft.com/en-us/azure/aks/istio-install).  
To enable istio on your kubernetes cluster, refer to the official [quick-start guide](https://istio.io/docs/setup/kubernetes/install/kubernetes/) or your specific kubernetes hosting solution guide.

##### Example - Presidio Service Metrics

- Make sure presidio namespace is tagged for istio sidecar injection and that presidio is deployed using the istio ingress.

    ```sh
    kubectl label namespace presidio istio-injection=enabled

    export REGISTRY=mcr.microsoft.com
    export TAG=latest
    
    helm install --name presidio-demo --set registry=$REGISTRY,tag=$TAG,api.ingress.enabled=true,api.ingress.class=istio charts/presidio --namespace presidio
    ```

- Open the grafana dashbaord

    ```sh
    kubectl -n istio-system port-forward $(kubectl -n istio-system get pod -l app=grafana -o jsonpath='{.items[0].metadata.name}') 3000:3000
    ```

- Open your browser at http://localhost:3000

- Istio's grafana comes with several built in dashabords, for instance:

    * **[Istio Mesh Dashboard](http://localhost:3000/dashboard/db/istio-mesh-dashboard)** - global view of the Mesh along with services and workloads in the mesh. 
    * **[Service Dashboards](http://localhost:3000/dashboard/db/istio-service-dashboard)** - metrics for the service and then client workloads (workloads that are calling this service) and service workloads (workloads that are providing this service) for that service.
    * **[Workload Dashboards](http://localhost:3000/dashboard/db/istio-workload-dashboard)** - metrics for each workload and then inbound workloads (workloads that are sending request to this workload) and outbound services (services to which this workload send requests) for that workload.


- Alternatively, open Prometheus dashabord to query the database directly

```sh
kubectl -n istio-system port-forward $(kubectl -n istio-system get pod -l app=prometheus -o jsonpath='{.items[0].metadata.name}') 9090:9090
```

- Open your browser at http://localhost:9090

-Search Prometheus for presidio containers telemetry

##### Example - Presidio Service Dependecies

- Open the [Kiali](https://www.kiali.io/) service mesh observability dashboard

```sh
kubectl port-forward -n istio-system $(kubectl get pod -n istio-system -l app=kiali -o jsonpath='{.items[0].metadata.name}') 20001:20001
```

- Open your browser at http://localhost:20001/kiali/console/

- View workload, application and service health and the dependency graph between presidio services with network and performance KPIs.   


##### Example - Presidio Distributed Metrics

- Open the [Jaeger](https://www.jaegertracing.io/) e2e distributed tracing tool

```sh
kubectl port-forward -n istio-system $(kubectl get pod -n istio-system -l app=jaeger -o jsonpath='{.items[0].metadata.name}') 16686:16686
```

- Open your browser at http://localhost:16686

- Note that jaeger has a sample rate of around 1/100, tracing may take time to show.

- Use the search tab to find specific requests and the dependencies tab to view presidio service relations.

### Using Linkerd

##### Enabling Linkerd on AKS

To enable linkerd on your kubernetes cluster, refer to the official [quick-start guide](https://linkerd.io/2/getting-started/) or your specific kubernetes hosting solution guide.

##### Example - Presidio Service Mesh Dashbaord and Metrics 

- Open the linkerd dashbaord

```sh
linkerd dashboard
```

- The browser is opened

- Linkerd dashbaord are built on top of prometheus and provide an overview of services health and KPIs.  
    grafana is opened when clicking a service for greater insights, featuring the following dashbaords:  

    * **Top Line Metrics** - "golden" KPIs for top services
    * **Deployment Detail** - per deployment KPIs
    * **Pod Details** - per pod KPIs
