#!/bin/bash
REGISTRY=${1:-presidio.azurecr.io}
TAG=${2:-latest}
helm install --name presidio-demo --set registry=$REGISTRY,tag=$TAG ../charts/presidio --namespace presidio
