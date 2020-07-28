#!/bin/bash
# This script is a helper to run the local docker build only. This does not deploy the service.
# There is no error checking in this script, it expects a local docker instance to be running.
# The make commands will take a very long time to run the first time as the docker images themselves
# take a long time to create. Expect to wait at least an hour or more, depending on machine and 
# network capabilities.



# Run the containers
DOCKER_REGISTRY=${DOCKER_REGISTRY:-"presidio"}
PRESIDIO_LABEL=${PRESIDIO_LABEL:-"latest"}
NETWORKNAME=${NETWORKNAME:-"presidio-network"}
NLP_CONF_PATH=${NLP_CONF_PATH:-"conf/default.yaml"}
if [[ ! "$(docker network ls)" =~ (^|[[:space:]])"$NETWORKNAME"($|[[:space:]]) ]]; then
    docker network create $NETWORKNAME
fi
docker run --rm --name redis --network $NETWORKNAME -d -p 6379:6379 redis
docker run --rm --name presidio-analyzer --network $NETWORKNAME -d -p 3000:3000 -e GRPC_PORT=3000 -e RECOGNIZERS_STORE_SVC_ADDRESS=presidio-recognizers-store:3004 -e NLP_CONF_PATH=${NLP_CONF_PATH} ${DOCKER_REGISTRY}/presidio-analyzer:${PRESIDIO_LABEL}
docker run --rm --name presidio-anonymizer --network $NETWORKNAME -d -p 3001:3001 -e GRPC_PORT=3001 ${DOCKER_REGISTRY}/presidio-anonymizer:${PRESIDIO_LABEL}
docker run --rm --name presidio-recognizers-store --network $NETWORKNAME -d -p 3004:3004 -e GRPC_PORT=3004 -e REDIS_URL=redis:6379 ${DOCKER_REGISTRY}/presidio-recognizers-store:${PRESIDIO_LABEL}

echo "waiting 30 seconds for analyzer model to load..."
sleep 30 # Wait for the analyzer model to load
docker run --rm --name presidio-api --network $NETWORKNAME -d -p 8080:8080 -e WEB_PORT=8080 -e ANALYZER_SVC_ADDRESS=presidio-analyzer:3000 -e ANONYMIZER_SVC_ADDRESS=presidio-anonymizer:3001 -e RECOGNIZERS_STORE_SVC_ADDRESS=presidio-recognizers-store:3004 ${DOCKER_REGISTRY}/presidio-api:${PRESIDIO_LABEL}
