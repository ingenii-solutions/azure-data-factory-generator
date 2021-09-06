config_table_storage = {
    "name": "AzureConfigTableStorage",
    "type": "Microsoft.DataFactory/factories/linkedservices",
    "properties": {
        "annotations": [],
        "type": "AzureTableStorage",
        "typeProperties": {
            "sasUri": {
                "type": "AzureKeyVaultSecret",
                "store": {
                    "referenceName": "Credentials Store",
                    "type": "LinkedServiceReference"
                },
                "secretName": "config-table-storage-sas-uri"
            }
        }
    }
}