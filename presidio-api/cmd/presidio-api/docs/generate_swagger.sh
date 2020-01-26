# chmod +x generate_swagger.sh
GO111MODULE=off swagger generate spec -o ./swagger.yaml --scan-models 
