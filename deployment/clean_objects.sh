#!/bin/bash

# Get the file name from the path
function getName() {
    echo "$1" | awk -F '/' '{ print $2 }' | sed 's/.json//'
}

# Set these to the details of the Data Factory you wish to update
RESOURCEGROUP=<resource group name>
DATAFACTORY=<data factory name>

IFS=$'\n' 

# Triggers
declare -a local_triggers
local_triggers=($(find trigger -type f -name "*.json" -print0 | xargs --null -I {} bash -c 'getName "$@"' _ {}))

declare -a remote_triggers
remote_triggers=($(az datafactory trigger list --resource-group "$RESOURCEGROUP" --factory-name "$DATAFACTORY" --query "[?properties.annotations!=null && contains(properties.annotations,'ManagedByIngeniiADFG')].name" -o tsv))

for remote in ${remote_triggers[@]}; do [[ "${IFS}${local_triggers[*]}${IFS}" =~ "${IFS}${remote}${IFS}" ]] || az datafactory trigger delete --resource-group "$RESOURCEGROUP" --factory-name "$DATAFACTORY" --name "$remote" --yes ; done

# Pipelines
declare -a local_pipelines
local_pipelines=($(find pipeline -type f -name "*.json" -print0 | xargs --null -I {} bash -c 'getName "$@"' _ {}))

declare -a remote_pipelines
remote_pipelines=($(az datafactory pipeline list --resource-group "$RESOURCEGROUP" --factory-name "$DATAFACTORY" --query "[?annotations!=null && contains(annotations,'ManagedByIngeniiADFG')].name" -o tsv))

for remote in ${remote_pipelines[@]}; do [[ "${IFS}${local_pipelines[*]}${IFS}" =~ "${IFS}${remote}${IFS}" ]] || az datafactory pipeline delete --resource-group "$RESOURCEGROUP" --factory-name "$DATAFACTORY" --name "$remote" --yes ; done

# Datasets
declare -a local_datasets
local_datasets=($(find dataset -type f -name "*.json" -print0 | xargs --null -I {} bash -c 'getName "$@"' _ {}))

declare -a remote_datasets
remote_datasets=($(az datafactory dataset list --resource-group "$RESOURCEGROUP" --factory-name "$DATAFACTORY" --query "[?properties.annotations!=null && contains(properties.annotations,'ManagedByIngeniiADFG')].name" -o tsv))

for remote in ${remote_datasets[@]}; do [[ "${IFS}${local_datasets[*]}${IFS}" =~ "${IFS}${remote}${IFS}" ]] || az datafactory dataset delete --resource-group "$RESOURCEGROUP" --factory-name "$DATAFACTORY" --dataset-name "$remote" --yes ; done

# Linked Services
declare -a local_linkedservices
local_linkedservices=($(find linkedService -type f -name "*.json" -print0 | xargs --null -I {} bash -c 'getName "$@"' _ {}))

declare -a remote_linkedservices
remote_linkedservices=($(az datafactory linked-service list --resource-group "$RESOURCEGROUP" --factory-name "$DATAFACTORY" --query "[?properties.annotations!=null && contains(properties.annotations,'ManagedByIngeniiADFG')].name" -o tsv))

for remote in ${remote_linkedservices[@]}; do [[ "${IFS}${local_linkedservices[*]}${IFS}" =~ "${IFS}${remote}${IFS}" ]] || az datafactory linked-service delete --resource-group "$RESOURCEGROUP" --factory-name "$DATAFACTORY" --linked-service-name "$remote" --yes ; done
