# Ingenii Azure Data Factory Generator
Python based generator to create Azure Data Factory pipelines from configurations.

This package integrates easily with the [Ingenii Azure Data Platform](https://github.com/ingenii-solutions/azure-data-platform), but this package can be used independently as long as some required linked services and data sets are created ahead of time. These are detailed in the sections below.

* Current Version: 0.1.3

## Package usage

Install the package [using pip](https://pip.pypa.io/en/stable/user_guide/) with 
```
pip install azure_data_factory_generator
```
or, for a particular version
```
pip install azure_data_factory_generator==0.1.3
```
Alternatively, add it to your `requirements.txt` file. 

Use the package by calling it directly with the locations of your config files and the folder that the generated objects should be placed within:
```
python -m azure_data_factory_generator path/to/config/files/folder path/to/generated/files/folder
```

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
        "frequency": "Day",
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
        1. Change the expiration data to be a long time in the future (e.g. 2100-01-01)
        1. Once the token is created, copy the `Table service SAS URL` version, which starts with `https://`
        1. Add this to the Key Vault with the secret name `datalake-table-storage-sas-uri`

## Triggers

As well as defining the pipeline itself, we need to define when it runs. At the moment only the 'Schedule' type of trigger has been implemented [out of the types available.](https://docs.microsoft.com/en-us/azure/data-factory/concepts-pipeline-execution-triggers)

All times are UTC. The option to change timezone has not yet been implemented.

### Recurrence

The most simple schedule is recurringly calling the pipeline after a fixed interval. The different approaches are:

```
    # Runs every 15 minutes
    "schedule": {
        "frequency": "Minute",
        "interval": "15"
    }

    # Runs every 3 hours
    "schedule": {
        "frequency": "Hour",
        "interval": "3"
    }

    # Runs every day at 6:00 AM
    "schedule": {
        "frequency": "Day",
        "time": "06:00"
    }

    # Daily frequency is assumed, so runs every day at 3:00 PM
    "schedule": {
        "time": "15:00"
    }
```

### Days of the week

Another approach is to set the days of the week the pipeline will run, and at which time. Times follow a cron-like approach where hours and minutes are set separately, and all combinations are run.

```
    # Runs every Tuesday, Thursday, and Sunday at 6:00 AM
    "schedule": {
        "hours": [6],
        "weekDays": [
            "Tuesday",
            "Thursday",
            "Sunday"
        ]
    }

    # Runs every Monday and Thursday, at 6:15, 6:30, 12:15, 12:30
    "schedule": {
        "hours": [6, 12],
        "minutes": [15, 30],
        "weekDays": [
            "Monday",
            "Thursday"
        ]
    }
```

### Days of the month

This approach runs the pipeline on certain days e.g. the third of the month. Similarly to the days fo the week, thhe hours and minutes are specified separately and follow a crom-like approach of combining all the permutations.

```
    # Runs on the 1st, 3rd, and 5th of each month at 6:00 AM
    "schedule": {
        "hours": [6],
        "monthDays": [1, 3, 5]
    }

    # Runs on the 10th, 13th, and 15th of each month at 6:15 AM and 7:15 AM
    "schedule": {
        "hours": [6, 7],
        "minutes": [15],
        "monthDays": [10, 13, 15]
    }
```

### Position in the month

This is the final option, where we can combine days of the week and month, for example 'The third Monday of each month'. This has not yet been implemented.

## Version History

* `0.1.0`: Initial package, FTP/SFTP connections with basic authentication
