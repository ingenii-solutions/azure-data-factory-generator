#!/bin/bash

# Set these to the details of the Data Factory you wish to update
RESOURCEGROUP=<resource group name>
DATAFACTORY=<data factory name>

FILES="integrationRuntime/*"
for f in $FILES
do
  az datafactory integration-runtime self-hosted create --resource-group "$RESOURCEGROUP" --factory-name "$DATAFACTORY" --integration-runtime-name "$(echo $f | awk -F '/' '{ print $2 }' | sed 's/.json//')" --compute-properties "$(cat $f | jq '.properties')"
done

FILES="linkedService/*"
for f in $FILES
do
  az datafactory linked-service create --resource-group "$RESOURCEGROUP" --factory-name "$DATAFACTORY" --linked-service-name "$(echo $f | awk -F '/' '{ print $2 }' | sed 's/.json//')" --properties "$(cat $f | jq '.properties')"
done

FILES="dataset/*"
for f in $FILES
do
  NAME="$(echo $f | awk -F '/' '{ print $2 }' | sed 's/.json//')"
  az datafactory dataset create --resource-group "$RESOURCEGROUP" --factory-name "$DATAFACTORY" --dataset-name "$NAME" --properties "$(cat $f | jq '.properties')"
done

FILES="pipeline/*"
for f in $FILES
do
  az datafactory pipeline create --resource-group "$RESOURCEGROUP" --factory-name "$DATAFACTORY" --name "$(echo "$f" | awk -F '/' '{ print $2 }' | sed 's/.json//')" --pipeline "$(cat "$f" | jq '.properties')"
done

FILES="trigger/*"
for f in $FILES
do
  az datafactory trigger create --resource-group "$RESOURCEGROUP" --factory-name "$DATAFACTORY" --trigger-name "$(echo $f | awk -F '/' '{ print $2 }' | sed 's/.json//')" --properties "$(cat $f | jq '.properties')"
done