sftp_basic_key_vault = {
    "name": "SFTPBasic",
    "properties": {
        "type": "Sftp",
        "parameters": {
            "Host": {
                "type": "String"
            },
            "KeyVaultSecretName": {
                "type": "String"
            },
            "UserName": {
                "type": "String"
            },
            "Port": {
                "type": "Int",
                "defaultValue": 22
            },
        },
        "annotations": [
            "ManagedByIngeniiADFG"
        ],
        "typeProperties": {
            "host": "@{linkedService().Host}",
            "port": "@linkedService().Port",
            "skipHostKeyValidation": True,
            "authenticationType": "Basic",
            "userName": "@{linkedService().UserName}",
            "password": {
                "type": "AzureKeyVaultSecret",
                "store": {
                    "referenceName": "Credentials Store",
                    "type": "LinkedServiceReference"
                },
                "secretName": "@{linkedService().KeyVaultSecretName}"
            }
        }
    }
}
