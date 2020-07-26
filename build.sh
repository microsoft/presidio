#!/bin/bash
# This script is a helper to run the local docker build only. This does not deploy the service.
# There is no error checking in this script, it expects a local docker instance to be running.
# The make commands will take a very long time to run the first time as the docker images themselves
# take a long time to create. Expect to wait at least an hour or more, depending on machine and 
# network capabilities.


# Build the images

DOCKER_REGISTRY=${DOCKER_REGISTRY:-presidio}
PRESIDIO_LABEL=${PRESIDIO_LABEL:-latest}
NETWORKNAME=${NETWORKNAME:-presidio-network}
make DOCKER_REGISTRY=${DOCKER_REGISTRY} PRESIDIO_LABEL=${PRESIDIO_LABEL} docker-build-deps
make DOCKER_REGISTRY=${DOCKER_REGISTRY} PRESIDIO_LABEL=${PRESIDIO_LABEL} docker-build
# Run the containers
NETWORKNAME=$NETWORKNAME DOCKER_REGISTRY="$DOCKER_REGISTRY" PRESIDIO_LABEL="$PRESIDIO_LABEL" ./run.sh
