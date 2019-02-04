#!/bin/bash

helm install --name redis stable/redis --set usePassword=false,rbac.create=true --namespace presidio-system --wait
helm install --name presidio-demo --set registry=$1,analyzer.tag=latest,anonymizer.tag=latest,anonymizerimage.tag=latest,ocr.tag=latest,scheduler.tag=latest,api.tag=latest,collector.tag=latest,datasink.tag=latest ../charts/presidio --namespace presidio
