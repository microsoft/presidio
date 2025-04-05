#!/bin/bash

# Check if both tenant ID and subscription ID are provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <tenant-id> <subscription-id> <resource-group>"
    exit 1
fi

TENANT_ID="$1"
SUBSCRIPTION_ID="$2"
RESOURCE_GROUP="$3"

az login --tenant "$TENANT_ID"
az account set --subscription "$SUBSCRIPTION_ID"
az deployment group create --resource-group "$RESOURCE_GROUP" --template-file main.bicep