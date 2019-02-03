#!/bin/bash

helm install --name redis stable/redis --set usePassword=false,rbac.create=true --namespace presidio-system --wait
kubectl create secret docker-registry acr-auth --docker-server $1 --docker-username $2 --docker-password $3 --docker-email some@email.com
helm install --name presidio-demo --set registry=$1,analyzer.tag=latest_stable_release,anonymizer.tag=latest_stable_release,anonymizerimage.tag=latest_stable_release,ocr.tag=latest_stable_release,scheduler.tag=latest_stable_release,api.tag=latest_stable_release,collector.tag=latest_stable_release,datasink.tag=latest_stable_release ..\charts\presidio --namespace presidio --wait
