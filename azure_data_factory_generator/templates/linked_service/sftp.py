sftp_basic_key_vault = {
	"name": "SFTPBasicKeyVault",
	"properties": {
		"type": "Sftp",
		"parameters": {
			"Host": {
				"type": "String"
			},
			"KeyVaultName": {
				"type": "String"
			},
			"KeyVaultSecretName": {
				"type": "String"
			},
			"UserName": {
				"type": "String"
			}
		},
		"annotations": [],
		"typeProperties": {
			"host": "@{linkedService().Host}",
			"port": 22,
			"skipHostKeyValidation": True,
			"authenticationType": "Basic",
			"userName": "@{linkedService().UserName}",
			"password": {
				"type": "AzureKeyVaultSecret",
				"store": {
					"referenceName": "@{linkedService().KeyVaultName}",
					"type": "LinkedServiceReference"
				},
				"secretName": "@{linkedService().KeyVaultSecretName}"
			}
		}
	}
}

linked_services_templates = {
    "sftp": {
        "basic": sftp_basic_key_vault
    }
}