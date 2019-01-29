helm install --name redis stable/redis --set usePassword=false,rbac.create=true --namespace presidio-system --wait
kubectl create secret docker-registry acr-auth --docker-server presidio.azurecr.io --docker-username <username> --docker-password <asppword> --docker-email some@email.com
helm repo add presidio 'https://raw.githubusercontent.com/Microsoft/presidio/deployment-script/charts/presidio'
helm repo update
helm install presidio/presidio --name presidio-demo --set registry=presidio.azurecr.io,analyzer.tag=1831,anonymizer.tag=1831,anonymizerimage.tag=1831,ocr.tag=1831,scheduler.tag=1831,api.tag=1831,collector.tag=1831,datasink.tag=1831 --namespace presidio --wait
