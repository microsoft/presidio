#!/bin/bash

# This script utilize KIND (https://github.com/kubernetes-sigs/kind), to install Presidio
# into docker (with k8s emulation).
# This script is intended to get Presidio up and running in no time, so you can play with it.
# However it is NOT intended to be installed in this manner for any workload (dev or prod).

# This script should be ran ONCE. if for anyreason a retry is needed.
# cleanup of the local environment is needed (kind delete cluster)

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