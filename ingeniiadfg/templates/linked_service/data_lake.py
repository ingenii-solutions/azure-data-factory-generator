data_lake = {
    "name": "DataLake",
    "type": "Microsoft.DataFactory/factories/linkedservices",
    "properties": {
        "annotations": [],
        "parameters": {
            "Name": {
                "type": "String"
            }
        },
        "type": "AzureBlobFS",
        "typeProperties": {
            "url": "https://@{linkedService().Name}.dfs.core.windows.net"
        }
    }
}
