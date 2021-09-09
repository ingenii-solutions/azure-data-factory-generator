from base import default_policy, DataFactoryPipeline


def get_key_vault_secret(secret_name):
    return {
        "name": "Get token",
        "type": "WebActivity",
        "dependsOn": [],
        "policy": {
            **default_policy,
            "secureOutput": True
        },
        "userProperties": [],
        "typeProperties": {
            "url": {
                "value": f"@concat('https://', pipeline().globalParameters.AzureKeyVaultName, '.vault.azure.net/secrets/{secret_name}?api-version=7.0')",
                "type": "Expression"
            },
            "method": "GET",
            "authentication": {
                "type": "MSI",
                "resource": "https://vault.azure.net"
            }
        }
    }


def create_token_header(get_token_activity, key="Authorization", value_prefix="Token "):
    return {
        "key": key,
        "value": {
            "value": f"@concat('{value_prefix}', activity('{get_token_activity['name']}').output.value)",
            "type": "Expression"
        }
    }


def copy_data(data_provider, table, base_url, path, output_type, headers=[], file_name_prefix='download_'):
    source = {
        "type": "RestSource",
        "httpRequestTimeout": "00:01:40",
        "requestInterval": "00.00:00:00.010",
        "requestMethod": "GET"
    }
    if headers:
        source["additionalHeaders"] = {
            header["key"]: header["value"]
            for header in headers
        }

    output = {
        "type": "DatasetReference",
        "parameters": {
            "data_provider": data_provider,
            "table": table,
            "file_name": {
                "value": f"@concat('{file_name_prefix}', utcnow('yyyy-MM-ddTHH:mm:ss'), '.csv')",
                "type": "Expression"
            }
        }
    }
    if output_type.lower() == "csv":
        output["referenceName"] = "RawCSV"
        output["parameters"]["header"] = True
    elif output_type.lower() == "json":
        output["referenceName"] = "RawJson"
    else:
        raise Exception(f"Don't recognise output type {output_type}!")

    return {
        "name": "Copy data to csv",
        "type": "Copy",
        "dependsOn": [],
        "policy": default_policy,
        "userProperties": [],
        "typeProperties": {
            "source": source,
            "sink": {
                "type": "DelimitedTextSink",
                "storeSettings": {
                    "type": "AzureBlobFSWriteSettings"
                },
                "formatSettings": {
                    "type": "DelimitedTextWriteSettings",
                    "quoteAllText": True,
                    "fileExtension": ".csv"
                }
            },
            "enableStaging": False
        },
        "inputs": [
            {
                "referenceName": "RestResource",
                "type": "DatasetReference",
                "parameters": {
                    "base_url": base_url,
                    "path": path,
                }
            }
        ],
        "outputs": [output]
    }


def generate_api_pipeline(data_provider, config, table):
    get_token = get_key_vault_secret(config["key_vault_secret_name"])

    authorization_header = create_token_header(get_token)

    copy_data_activity = copy_data(
        data_provider, table["name"],
        config["base_url"], table["path"], config["output_type"], headers=[authorization_header])
