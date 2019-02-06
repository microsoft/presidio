#!/bin/bash
REGISTRY=${1:-presidio.azurecr.io}
TAG=${2:-latest}

echo $REGISTRY
echo $TAG
helm install --name redis stable/redis --set usePassword=false,rbac.create=true --namespace presidio-system --wait
helm install --name presidio-demo --set registry=$REGISTRY,analyzer.tag=$TAG,anonymizer.tag=$TAG,anonymizerimage.tag=$TAG,ocr.tag=$TAG,scheduler.tag=$TAG,api.tag=$TAG,collector.tag=$TAG,datasink.tag=$TAG ../charts/presidio --namespace presidio
