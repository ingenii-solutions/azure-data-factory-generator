config_table = {
    "name": "ConfigTable",
    "properties": {
        "linkedServiceName": {
            "referenceName": "AzureConfigTableStorage",
            "type": "LinkedServiceReference"
        },
        "parameters": {
            "TableName": {
                "type": "string"
            }
        },
        "annotations": [
            "ManagedByIngeniiADFG"
        ],
        "type": "AzureTable",
        "schema": [],
        "typeProperties": {
            "tableName": {
                "value": "@dataset().TableName",
                "type": "Expression"
            }
        }
    },
    "type": "Microsoft.DataFactory/factories/datasets"
}
