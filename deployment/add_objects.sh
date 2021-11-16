#!/bin/bash

# Get the file name from the path
function getName() {
    echo "$1" | awk -F '/' '{ print $2 }' | sed 's/.json//'
}

# Set these to the details of the Data Factory you wish to update
RESOURCEGROUP=<resource group name>
DATAFACTORY=<data factory name>

find integrationRuntime -type f -name "*.json" -print0 | while IFS= read -r -d '' file; do
  if [[ $(cat "$file" | jq '.properties.type' | sed 's/"//g') == "SelfHosted" ]] 
  then
    az datafactory integration-runtime self-hosted create --resource-group "$RESOURCEGROUP" --factory-name "$DATAFACTORY" --integration-runtime-name "$(getName "$file")"
  fi
done

find linkedService -type f -name "*.json" -print0 | while IFS= read -r -d '' file; do
  az datafactory linked-service create --resource-group "$RESOURCEGROUP" --factory-name "$DATAFACTORY" --linked-service-name "$(getName "$file")" --properties "$(cat "$file" | jq '.properties')"
done

find dataset -type f -name "*.json" -print0 | while IFS= read -r -d '' file; do
  az datafactory dataset create --resource-group "$RESOURCEGROUP" --factory-name "$DATAFACTORY" --dataset-name "$(getName "$file")" --properties "$(cat "$file" | jq '.properties')"
done

find pipeline -type f -name "*.json" -print0 | while IFS= read -r -d '' file; do
  az datafactory pipeline create --resource-group "$RESOURCEGROUP" --factory-name "$DATAFACTORY" --name "$(getName "$file")" --pipeline "$(cat "$file" | jq '.properties')"
done

find trigger -type f -name "*.json" -print0 | while IFS= read -r -d '' file; do
  az datafactory trigger create --resource-group "$RESOURCEGROUP" --factory-name "$DATAFACTORY" --trigger-name "$(getName "$file")" --properties "$(cat "$file" | jq '.properties')"
done
