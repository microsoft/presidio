git clone https://github.com/kubernetes-sigs/kind.git
cd kind
make build

kind create cluster

kubectl create namespace presidio

cd ..
./deploy-helm.sh
./deploy-presidio.sh

