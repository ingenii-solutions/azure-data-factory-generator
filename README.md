# Ingenii Azure Data Factory Generator
Python based generator to create Azure Data Factory pipelines from configurations.

This package integrates easily with the [Ingenii Azure Data Platform](https://github.com/ingenii-solutions/azure-data-platform), but this package can be used independently as long as some required linked services and data sets are created ahead of time. These are detailed in the sections below.

* Current Version: 0.1.0

## Connections

### <a name="general_requirements"></a>General requirements

If not using the Ingenii Azure Data Platform, then there are some resources that need to be created ahead of using this package, as these are assumed to exist already. The below are used by all different pipelines.

1. A key vault linked service called `Credentials Store`, where credentials and secrets are drawn from. 
    1. It's recommended that the Data Factory managed identity is used to connect to the Key Vault
    1. The Data Factory requires `Get` credentials to the `Secrets` key vault type.
1. A data lake linked service called `Data Lake`:
    1. In the data lake itself, a container called `raw` which the files will be moved to

### FTP/SFTP

#### Example configuration
```
{
    "name": "example-data-provider",
    "connection": "ftp",
    "authentication": "basic",
    "self_hosted_integration_runtime": "adp-self-hosted",
    "config": {
        "host": "hostaddress.com",
        "username": "username-321",
        "key_vault_secret_name": "example-data-provider-password"
    },
    "schedule": {
        "recurrence": "day",
        "time": "06:00"
    },
    "tables": [
        {
            "name": "table1",
            "path": "/path1"
        }
    ]
}
```
#### Requirements

As well as those listed in the [General requirements](#general_requirements), these are specific to the FTP/SFTP pipelines that should be created ahead of time:

1. Add to the data lake referenced by the linked service `Data Lake`:
    1. A table in table storage called `KnownSFTPFiles` where we keep track of which files have been processed
    1. A table called `Select1`, with an entry with PartitionKey `1` and RowKey `1`, for adding new entries to the `KnownSFTPFiles` table
1. Add to the key vault referenced by the linked service `Credentials Store`:
    1. The server password as a secret, with the name you have given in the config JSON at `config.key_vault_secret_name`
    1. A [SAS token](https://docs.microsoft.com/en-us/azure/storage/common/storage-sas-overview) that grants access to the table storage in the data lake referenced by the linked service `Data Lake`.
        1. [Guide to creating a SAS token manually](https://docs.microsoft.com/en-us/azure/cognitive-services/translator/document-translation/create-sas-tokens?tabs=Containers)
        1. `Allowed services` should be restricted to `Table`
        1. `Allowed resource types` should be restricted to `Object`
        1. All possible permissions should be added
        1. Change the expiration data to be a long time in the future (~2100)
        1. Once the token is created, copy the `Table service SAS URL` version, which starts with `https://`
        1. The secret name should be `config-table-storage-sas-uri`

## Version History

* `0.1.0`: Initial package, FTP/SFTP connections with basic authentication
