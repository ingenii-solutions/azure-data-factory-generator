#!/bin/bash

# Get the file name from the path
function getName() {
    echo "$1" | awk -F '/' '{ print $2 }' | sed 's/.json//'
}

# Set these to the details of the Data Factory you wish to update
RESOURCEGROUP=<resource group name>
DATAFACTORY=<data factory name>

# Triggers
declare -a local_triggers
FILES="trigger/*"
find trigger -type f -name "*.json" -print0 | while IFS= read -r -d '' file; do local_triggers[${#local_triggers[@]}+1]=$(getName "$t"); done

declare -a remote_triggers
remote_triggers=($(az datafactory trigger list --resource-group "$RESOURCEGROUP" --factory-name "$DATAFACTORY" --query "[?properties.annotations!=null && contains(properties.annotations,'ManagedByIngeniiADFG')]"))

for remote in ${remote_triggers[@]}; do [[ " ${local_triggers[*]} " =~ " ${remote} " ]] || az datafactory trigger delete --resource-group "$RESOURCEGROUP" --factory-name "$DATAFACTORY" --name $remote --yes ; done

# Pipelines
declare -a local_pipelines
find pipeline -type f -name "*.json" -print0 | while IFS= read -r -d '' file; do local_pipelines[${#local_pipelines[@]}+1]=$(getName "$t"); done

declare -a remote_pipelines
remote_pipelines=($(az datafactory pipeline list --resource-group "$RESOURCEGROUP" --factory-name "$DATAFACTORY" --query "[?properties.annotations!=null && contains(properties.annotations,'ManagedByIngeniiADFG')]"))

for remote in ${remote_pipelines[@]}; do [[ " ${local_pipelines[*]} " =~ " ${remote} " ]] || az datafactory pipeline delete --resource-group "$RESOURCEGROUP" --factory-name "$DATAFACTORY" --name $remote --yes ; done

# Datasets
declare -a local_datasets
find dataset -type f -name "*.json" -print0 | while IFS= read -r -d '' file; do local_datasets[${#local_datasets[@]}+1]=$(getName "$t");
done

declare -a remote_datasets
remote_datasets=($(az datafactory dataset list --resource-group "$RESOURCEGROUP" --factory-name "$DATAFACTORY" --query "[?properties.annotations!=null && contains(properties.annotations,'ManagedByIngeniiADFG')]"))

for remote in ${remote_datasets[@]}; do [[ " ${local_datasets[*]} " =~ " ${remote} " ]] || az datafactory dataset delete --resource-group "$RESOURCEGROUP" --factory-name "$DATAFACTORY" --dataset-name $remote --yes ; done

# Linked Services
declare -a local_linkedservices
find linkedService -type f -name "*.json" -print0 | while IFS= read -r -d '' file; do   local_linkedservices[${#local_linkedservices[@]}+1]=$(getName "$t"); done

declare -a remote_linkedservices
remote_linkedservices=($(az datafactory linked-service list --resource-group "$RESOURCEGROUP" --factory-name "$DATAFACTORY" --query "[?properties.annotations!=null && contains(properties.annotations,'ManagedByIngeniiADFG')]"))

for remote in ${remote_linkedservices[@]}; do [[ " ${local_linkedservices[*]} " =~ " ${remote} " ]] || az datafactory linked-service delete --resource-group "$RESOURCEGROUP" --factory-name "$DATAFACTORY" --linked-service-name $remote --yes ; done
