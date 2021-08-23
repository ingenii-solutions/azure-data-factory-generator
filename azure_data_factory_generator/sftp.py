from .activities.data_lake import get_data_lake_files
from .activities.generic import filter_for_files
from .base import DataFactoryPipeline
from .templates.linked_service.data_lake import data_lake
from .templates.linked_service.sftp import sftp_basic_key_vault
from .templates.dataset.data_lake import data_lake_folder
from .templates.dataset.sftp import sftp_folder, sftp_file

class SFTPPipeline(DataFactoryPipeline):

    name = "sftp"
    authentications = {
        "basic": {
            "required_config" : ["host", "username", "key_vault_name", "key_vault_secret"],
            "linked_service": sftp_basic_key_vault
        }
    }
    source_data_sets = {
        "source_folder": sftp_folder, 
        "source_file" : sftp_file
    }
    target_linked_service = data_lake
    target_data_sets = {
        "target_folder": data_lake_folder
    }

    required_table_parameters = ["name", "path"]
    # TODO: implement prefix and suffix checks
    #optional_table_parameters = ["zipped", "prefix", "suffix"]

    def __init__(self, data_provider, authentication, 
                 config, table_definition, data_sets):
        self.data_provider = data_provider
        self.authentication = authentication
        self.config = config
        self.table_definition = table_definition
        self.data_sets = data_sets

        self.data_lake_path = self.data_provider + "/" + self.table_definition["name"]

        super(SFTPPipeline, self).__init__(self.data_lake_path.replace("/", "-"))        

    def list_sftp_files(self):
        return {
            "name": f"List files at {self.table_definition['path']}".replace("/", "-"),
            "type": "GetMetadata",
            "dependsOn": [],
            "policy": self.default_policy,
            "userProperties": [],
            "typeProperties": {
                "dataset": {
                    "referenceName": self.data_sets["source_folder"],
                    "type": "DatasetReference",
                    "parameters": {
                        "Host": self.config["host"],
                        "UserName": self.config["username"],
                        "KeyVaultName": self.config["key_vault_name"],
                        "KeyVaultSecretName": self.config["key_vault_secret_name"],
                        "FolderPath": self.table_definition["path"]
                    }
                },
                "fieldList": [
                    "childItems"
                ],
                "storeSettings": {
                    "type": "SftpReadSettings",
                    "recursive": True,
                    "enablePartitionDiscovery": False
                },
                "formatSettings": {
                    "type": "BinaryReadSettings"
                }
            }
        }


    def move_new_files(self):
        return {
            "name": "For each found file",
            "type": "ForEach",
            "dependsOn": [
                {
                    "activity": activity["name"],
                    "dependencyConditions": [
                        "Succeeded"
                    ]
                }
                for activity in [self.source_files] + self.known_file_activities
            ],
            "userProperties": [],
            "typeProperties": {
                "items": {
                    "value": f"@activity('{self.source_files['name']}').output.childItems",
                    "type": "Expression"
                },
                "activities": [
                    {
                        "name": "If new file",
                        "type": "IfCondition",
                        "dependsOn": [],
                        "userProperties": [],
                        "typeProperties": {
                            "expression": {
                                "value": f"@not(or(contains(activity('{self.known_file_activities[0]['name']}').output.childItems, item()), contains(activity('{self.known_file_activities[1]['name']}').output.childItems, item())))",
                                "type": "Expression"
                            },
                            "ifTrueActivities": [
                                {
                                    "name": "Move file to raw",
                                    "type": "Copy",
                                    "dependsOn": [],
                                    "policy": self.default_policy,
                                    "userProperties": [],
                                    "typeProperties": {
                                        "source": {
                                            "type": "BinarySource",
                                            "storeSettings": {
                                                "type": "SftpReadSettings",
                                                "recursive": False,
                                                "deleteFilesAfterCompletion": False
                                            },
                                            "formatSettings": {
                                                "type": "BinaryReadSettings"
                                            }
                                        },
                                        "sink": {
                                            "type": "BinarySink",
                                            "storeSettings": {
                                                "type": "AzureBlobFSWriteSettings"
                                            }
                                        },
                                        "enableStaging": False
                                    },
                                    "inputs": [
                                        {
                                            "referenceName": self.data_sets["source_file"],
                                            "type": "DatasetReference",
                                            "parameters": {
                                                "Host": self.config["host"],
                                                "UserName": self.config["username"],
                                                "KeyVaultName": self.config["key_vault_name"],
                                                "KeyVaultSecretName": self.config["key_vault_secret_name"],
                                                "FolderPath": self.table_definition["path"],
                                                "FileName": {
                                                    "value": "@item().name",
                                                    "type": "Expression"
                                                },
                                            }
                                        }
                                    ],
                                    "outputs": [
                                        {
                                            "referenceName": self.data_sets["target_folder"],
                                            "type": "DatasetReference",
                                            "parameters": {
                                                "Container": "raw",
                                                "FolderPath": self.data_lake_path
                                            }
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                ]
            }
        }

    def generate_pipeline(self):

        # --

        self.source_files = self.list_sftp_files()
        self.add_activity(self.source_files)
        
        # --

        find_all_raw_files = get_data_lake_files(
            self.default_policy, self.data_sets["target_folder"], 
            "raw", self.data_lake_path)
        find_all_archive_files = get_data_lake_files(
            self.default_policy, self.data_sets["target_folder"], 
            "archive", self.data_lake_path)

        self.add_activity(find_all_raw_files)
        self.add_activity(find_all_archive_files)

        # --

        find_raw_files = filter_for_files(find_all_raw_files)
        find_archive_files = filter_for_files(find_all_archive_files)

        self.add_activity(find_raw_files, depends_on=[find_all_raw_files])
        self.add_activity(find_archive_files, depends_on=[find_all_archive_files])

        self.known_file_activities = [find_raw_files, find_archive_files] 

        # --

        move_files = self.move_new_files()
        self.add_activity(move_files, depends_on=[self.source_files] + self.known_file_activities)
