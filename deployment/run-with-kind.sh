#!/bin/bash

# This script utilize KIND (https://github.com/kubernetes-sigs/kind), to install Presidio
# into docker (with k8s emulation).
# This script is intended to get Presidio up and running in no time, so you can play with it.
# However it is NOT intended to be installed in this manner for any workload (dev or prod).

# Clone KIND and build it (this way we eliminate the need to have GO installed)
git clone https://github.com/kubernetes-sigs/kind.git
cd kind
make build

# Create a KIND cluster into which we will deploy Presidio
bin/kind create cluster

# Create a namespace
kubectl create namespace presidio

# Install Presidio
cd ..
./deploy-helm.sh
./deploy-presidio.sh

kubectl wait --for=condition=ready pod -l app=presidio-demo-presidio-api -n presidio

kubectl port-forward presidio-demo-presidio-api 8080:8080 -n presidio
