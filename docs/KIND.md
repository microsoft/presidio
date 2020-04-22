# Run Presidio locally with KIND

Presidio is built for Kubernetes, you can give it a try using [KIND (Kubernetes IN Docker)](https://github.com/kubernetes-sigs/kind).

1. Install [Docker](https://docs.docker.com/install/).

   - **Optional (Linux)** - the following command will install all prerequisites (Docker, Helm, make, kubetl).

     ```sh
     cd deployment/
     ./prerequisites.sh
     ```

     depending on your environment, sudo might be needed

2. Clone Presidio.

3. Run the following script, which will use KIND (Kubernetes emulation in Docker)

   ```sh
   cd deployment/
   ./run-with-kind.sh
   ```

4. Wait and verify all pods are running:

   ```sh
   kubectl get pod -n presidio
   ```

5. Port forwarding of HTTP requests to the API micro-service will be done automatically. In order to run manual:
   ```sh
   kubectl port-forward <presidio-api-pod-name> 8080:8080 -n presidio
   ```
