helm install --name redis stable/redis --set usePassword=false,rbac.create=true --namespace presidio-system --wait
kubectl create secret docker-registry acr-auth --docker-server presidio.azurecr.io --docker-username <username> --docker-password <password> --docker-email some@email.com
helm repo add presidio 'https://raw.githubusercontent.com/Microsoft/presidio/deployment-script/charts/presidio'
helm repo update
helm install presidio/presidio --name presidio-demo --set registry=presidio.azurecr.io,analyzer.tag=latest_stable_release,anonymizer.tag=latest_stable_release,anonymizerimage.tag=latest_stable_release,ocr.tag=latest_stable_release,scheduler.tag=latest_stable_release,api.tag=latest_stable_release,collector.tag=latest_stable_release,datasink.tag=latest_stable_release --namespace presidio --wait
