#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset
# set -o xtrace # For debugging

# REQUIRED VARIABLES:
#
# DATABRICKS_WORKSPACE_URL
# DATABRICKS_WORKSPACE_ID
# STORAGE_ACCOUNT_NAME
# STORAGE_CONTAINER_NAME
# RESOURCE_GROUP

get_pat () {
    declare message=$1
    # Retrieve databricks PAT token
    echo "Generating a Databricks PAT token."
    databricks_global_token=$(az account get-access-token --resource 2ff814a6-3304-4ab8-85cb-cd0e6f879c1d --output json | jq -r .accessToken) # Databricks app global id
    azure_api_token=$(az account get-access-token --resource https://management.core.windows.net/ --output json | jq -r .accessToken)
    api_response=$(curl -sf $DATABRICKS_HOST/api/2.0/token/create \
    -H "Authorization: Bearer $databricks_global_token" \
    -H "X-Databricks-Azure-SP-Management-Token:$azure_api_token" \
    -H "X-Databricks-Azure-Workspace-Resource-Id:$DATABRICKS_WORKSPACE_ID" \
    -d "{ \"comment\": \"$message\" }")
    databricks_token=$(echo $api_response | jq -r '.token_value')
    export DATABRICKS_TOKEN=$databricks_token
}

cluster_exists () {
    declare cluster_name="$1"
    declare cluster=$(databricks clusters list | tr -s " " | cut -d" " -f2 | grep ^${cluster_name}$)
    if [[ -n $cluster ]]; then
        return 0; # cluster exists
    else
        return 1; # cluster does not exists
    fi
}

wait_for_run () {
    # See here: https://docs.azuredatabricks.net/api/latest/jobs.html#jobsrunresultstate
    declare mount_run_id=$1
    while : ; do
        life_cycle_status=$(databricks runs get --run-id $mount_run_id | jq -r ".state.life_cycle_state") 
        result_state=$(databricks runs get --run-id $mount_run_id | jq -r ".state.result_state")
        if [[ $result_state == "SUCCESS" || $result_state == "SKIPPED" ]]; then
            break;
        elif [[ $life_cycle_status == "INTERNAL_ERROR" || $result_state == "FAILED" ]]; then
            state_message=$(databricks runs get --run-id $mount_run_id | jq -r ".state.state_message")
            echo -e "${RED}Error while running ${mount_run_id}: ${state_message} ${NC}"
            exit 1
        else 
            echo "Waiting for run ${mount_run_id} to finish..."
            sleep 1m
        fi
    done
}

wait_for_cluster () {
    declare cluster_id=$1
    while : ; do
        cluster_state=$(databricks clusters get --cluster-id $cluster_id | jq -r ".state") 
        if [[ $cluster_state == "RUNNING" ]]; then
            break;
        elif [[ $cluster_state == "TERMINATED" || $cluster_state == "ERROR" ]]; then
            state_message=$(databricks clusters get --cluster-id $cluster_id | jq -r ".state_message")
            echo -e "${RED}Error while creating ${cluster_id}: ${state_message} ${NC}"
            exit 1
        else 
            echo "Waiting for cluster ${cluster_id} to be ready..."
            sleep 1m
        fi
    done
}

export DATABRICKS_HOST=https://$DATABRICKS_WORKSPACE_URL
get_pat "For Deployment"

# Getting storage primary key
storage_primary_key=$(az storage account keys list -g $RESOURCE_GROUP -n $STORAGE_ACCOUNT_NAME --output json| jq -r .[0].value)

echo "Configuring Databricks workspace"

# Setting up databricks backed secret scope and secrets
echo "Setting up secrets"
databricks secrets create-scope --scope storage_scope --initial-manage-principal users || true
databricks secrets put --scope storage_scope --key storage_account_access_key --string-value "$storage_primary_key"

# Upload the init script to the file system
echo "Uploading init scripts"
databricks fs cp "./setup/startup.sh" "dbfs:/FileStore/dependencies/startup.sh" || true

# Upload notebooks
echo "Uploading notebooks"
databricks workspace import_dir "./notebooks" "/notebooks" --overwrite

# Create Cluster
cluster_config=$(cat "./config/cluster.config.json")
cluster_name=$(echo $cluster_config | jq -r .cluster_name)
echo "Creating a cluster $cluster_name"
if cluster_exists $cluster_name ; then
    echo "Cluster $cluster_name already exists!"
    cluster_id=$(databricks clusters get --cluster-name $cluster_name | jq -r .cluster_id)
else
    cluster_config=$(echo $cluster_config | jq --arg variable "$STORAGE_ACCOUNT_NAME" '.spark_env_vars.STORAGE_ACCOUNT_NAME = $variable')
    cluster_config=$(echo $cluster_config | jq --arg variable "$STORAGE_CONTAINER_NAME" '.spark_env_vars.STORAGE_CONTAINER_NAME = $variable')
    
    echo "Creating cluster $cluster_name with config $cluster_config. This may take a while as cluster spins up..."
    cluster_id=$(databricks clusters create --json "$cluster_config" | jq -r .cluster_id)
    echo "Waiting for Databricks cluster $cluster_id to be ready..."
    wait_for_cluster $cluster_id
fi

# Setup mount by running notebook
echo "Setting up Azure Storage mount"
run_config=$(cat "./config/run.setup.config.json")
run_config=$(echo $run_config | jq --arg variable "$cluster_id" '.existing_cluster_id = $variable')
echo "Running setup job on cluster $cluster_name with config $run_config. This may take a while..."
wait_for_run $(databricks runs submit --json "$run_config" | jq -r ".run_id" )

get_pat "For CLI"
echo $DATABRICKS_TOKEN