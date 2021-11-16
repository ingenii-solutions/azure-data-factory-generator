#!/bin/bash

# Set these to the details of the Data Factory you wish to update
RESOURCEGROUP=<resource group name>
DATAFACTORY=<data factory name>

# Triggers
declare -a local_triggers
FILES="trigger/*"
for t in $FILES; do local_triggers[${#local_triggers[@]}+1]=$(echo "$t" | awk -F '/' '{ print $2 }' | sed 's/.json//'); done

declare -a remote_triggers
remote_triggers=($(az datafactory trigger list --resource-group "$RESOURCEGROUP" --factory-name "$DATAFACTORY" --query "[?properties.annotations!=null && contains(properties.annotations,'ManagedByIngeniiADFG')]"))

for remote in ${remote_triggers[@]}; do [[ " ${local_triggers[*]} " =~ " ${remote} " ]] || az datafactory trigger delete --resource-group "$RESOURCEGROUP" --factory-name "$DATAFACTORY" --name $remote --yes ; done

# Pipelines
declare -a local_pipelines
FILES="pipeline/*"
for t in $FILES; do local_pipelines[${#local_pipelines[@]}+1]=$(echo "$t" | awk -F '/' '{ print $2 }' | sed 's/.json//'); done

declare -a remote_pipelines
remote_pipelines=($(az datafactory pipeline list --resource-group "$RESOURCEGROUP" --factory-name "$DATAFACTORY" --query "[?properties.annotations!=null && contains(properties.annotations,'ManagedByIngeniiADFG')]"))

for remote in ${remote_pipelines[@]}; do [[ " ${local_pipelines[*]} " =~ " ${remote} " ]] || az datafactory pipeline delete --resource-group "$RESOURCEGROUP" --factory-name "$DATAFACTORY" --name $remote --yes ; done

# Datasets
declare -a local_datasets
FILES="dataset/*"
for t in $FILES; do local_datasets[${#local_datasets[@]}+1]=$(echo "$t" | awk -F '/' '{ print $2 }' | sed 's/.json//'); done

declare -a remote_datasets
remote_datasets=($(az datafactory dataset list --resource-group "$RESOURCEGROUP" --factory-name "$DATAFACTORY" --query "[?properties.annotations!=null && contains(properties.annotations,'ManagedByIngeniiADFG')]"))

for remote in ${remote_datasets[@]}; do [[ " ${local_datasets[*]} " =~ " ${remote} " ]] || az datafactory dataset delete --resource-group "$RESOURCEGROUP" --factory-name "$DATAFACTORY" --dataset-name $remote --yes ; done

# Linked Services
declare -a local_linkedservices
FILES="linked-service/*"
for t in $FILES; do local_linkedservices[${#local_linkedservices[@]}+1]=$(echo "$t" | awk -F '/' '{ print $2 }' | sed 's/.json//'); done

declare -a remote_linkedservices
remote_linkedservices=($(az datafactory linked-service list --resource-group "$RESOURCEGROUP" --factory-name "$DATAFACTORY" --query "[?properties.annotations!=null && contains(properties.annotations,'ManagedByIngeniiADFG')]"))

for remote in ${remote_linkedservices[@]}; do [[ " ${local_linkedservices[*]} " =~ " ${remote} " ]] || az datafactory linked-service delete --resource-group "$RESOURCEGROUP" --factory-name "$DATAFACTORY" --linked-service-name $remote --yes ; done
