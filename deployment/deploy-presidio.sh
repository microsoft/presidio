#!/bin/bash

helm install --name redis stable/redis --set usePassword=false,rbac.create=true --namespace presidio-system --wait
kubectl create secret docker-registry acr-auth --docker-server $1 --docker-username $2 --docker-password $3 --docker-email some@email.com
helm install --name presidio-demo --set registry=$1,analyzer.tag=latest,anonymizer.tag=latest,anonymizerimage.tag=latest,ocr.tag=latest,scheduler.tag=latest,api.tag=latest,collector.tag=latest,datasink.tag=latest ../charts/presidio --namespace presidio
