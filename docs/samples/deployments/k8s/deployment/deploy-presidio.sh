#!/bin/bash
REGISTRY=${1:-mcr.microsoft.com}
TAG=${2:-latest}
RELEASE=${3:-demo}
helm install $RELEASE --set registry=$REGISTRY,tag=$TAG ../charts/presidio --namespace presidio