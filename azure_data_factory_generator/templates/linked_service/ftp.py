ftp_basic_key_vault = {
    "name": "FTPBasic",
    "properties": {
        "type": "FtpServer",
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
                "defaultValue": 21
            },
        },
        "annotations": [
            "ManagedByIngeniiADFG"
        ],
        "typeProperties": {
            "host": "@{linkedService().Host}",
            "port": "@linkedService().Port",
            "enableSsl": True,
            "enableServerCertificateValidation": True,
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
