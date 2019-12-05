#!/bin/bash
REGISTRY=${1:-mcr.microsoft.com}
TAG=${2:-latest}
helm install redis stable/redis --set usePassword=false,rbac.create=true --namespace presidio-system --wait
helm install presidio-demo --set registry=$REGISTRY,tag=$TAG ../charts/presidio --namespace presidio
