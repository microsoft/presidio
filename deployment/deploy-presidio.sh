#!/bin/bash
REGISTRY=${1:-mcr.microsoft.com}
TAG=${2:-latest}
helm install demo --set registry=$REGISTRY,tag=$TAG ../charts/presidio --namespace presidio