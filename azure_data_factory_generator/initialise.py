from copy import deepcopy
import json
from os import listdir, makedirs, mkdir, path

from .sftp import SFTPPipeline

class CreateDataFactoryObjects:

    connection_types = {
        "sftp": SFTPPipeline
    }
    all_config_jsons = []

    def __init__(self, config_folder=None, generated_folder=None):
        self.config_folder = config_folder or "configs"
        self.generated_folder = generated_folder or "generated"

        self.linked_service_folder = f"{self.generated_folder}/linkedService"
        self.data_set_folder = f"{self.generated_folder}/dataset"
        self.pipeline_folder = f"{self.generated_folder}/pipeline"

        self.check_folders()

    def check_folders(self):
        for folder in [self.linked_service_folder, self.data_set_folder, self.pipeline_folder]:
            if not path.exists(folder):
                makedirs(folder)

    def get_configs(self):
        if not self.all_config_jsons:
            # all_configs = listdir(self.config_folder)
            # Pretend this is all configs
            all_configs = ["sftp_basic.json"]
            for config_file_name in all_configs:
                with open(f"{self.config_folder}/{config_file_name}", "r") as json_file:
                    self.all_config_jsons.append(json.load(json_file))

        for config_json in self.all_config_jsons:
            yield config_json

    @staticmethod
    def find_all_connections(config_jsons):
        # Find all unique instances of connection and authentication types
        types = {}
        for config in config_jsons:
            connection, authentication = config["connection"], config["authentication"]
            types[connection] = \
                types.get(connection, set()) | set([authentication])
        return types

        # Validation of configs

    all_linked_services = {}

    def find_required_linked_services(self):
        # Find only the required linked services
        all_source_linked_services = {}
        for conn, auths in self.find_all_connections(self.get_configs()).items():

            if conn not in all_source_linked_services:
                all_source_linked_services[conn] = {}
            
            target_linked_service = self.connection_types[conn].target_linked_service
            self.all_linked_services[target_linked_service["name"]] = target_linked_service

            for auth in auths:
                source_linked_service = self.connection_types[conn].authentications[auth]["linked_service"]
                self.all_linked_services[source_linked_service["name"]] = source_linked_service
                all_source_linked_services[conn][auth] = source_linked_service

        return all_source_linked_services
    
    def write_json(self, file_path, json_to_write):
        with open(file_path, "w") as json_file:
            json.dump(json_to_write, json_file, indent=4)

    def write_linked_service_file(self, linked_service_json):
        self.write_json(
            f"{self.linked_service_folder}/{linked_service_json['name']}.json",
            linked_service_json
        )

    def write_data_set_file(self, data_set_json):
        self.write_json(
            f"{self.data_set_folder}/{data_set_json['name']}.json",
            data_set_json
        )

    def write_pipeline_file(self, pipeline_json):
        self.write_json(
            f"{self.pipeline_folder}/{pipeline_json['name']}.json",
            pipeline_json
        )

    all_data_sets = {}

    def generate_data_set_json(self, connection_type, linked_service_json, data_set_template):
        ds_id = (linked_service_json["name"], data_set_template["name"])
        if ds_id not in self.all_data_sets:

            data_set_json = deepcopy(data_set_template)

            ds_name = data_set_json["name"]
            print(ds_name.lower(), linked_service_json["name"].lower())
            if ds_name.lower().startswith(linked_service_json["name"].lower()):
                ds_name = ds_name[len(linked_service_json["name"]):]
            if ds_name.lower().startswith(connection_type.lower()):
                ds_name = ds_name[len(connection_type):]
            
            data_set_json["name"] = linked_service_json["name"] + ds_name

            # Add linked service definition, including required parameters
            data_set_json["properties"]["linkedServiceName"] = {
                "referenceName": linked_service_json["name"],
                "type": "LinkedServiceReference",
                "parameters": {
                    param: {
                        "value": f"@dataset().{param}",
                        "type": "Expression"
                    }
                    for param in linked_service_json["properties"]["parameters"]
                }
            }
            # Add linked service parameters to data set parameters
            for param, val in linked_service_json["properties"]["parameters"].items():
                data_set_json["properties"]["parameters"][param] = val
            
            self.all_data_sets[ds_id] = data_set_json
        return self.all_data_sets[ds_id]

    def find_data_sets_per_type(self, linked_services_by_type):
        data_sets_per_type = {}

        # Generate the data sets per linked service
        for conn, auths in linked_services_by_type.items():

            data_sets_per_type[conn] = {}

            for auth, linked_service_json in auths.items():

                data_sets_per_type[conn][auth] = {}

                for data_set_id, data_set_json in self.connection_types[conn].source_data_sets.items():
                    data_sets_per_type[conn][auth][data_set_id] = self.generate_data_set_json(
                        conn, linked_service_json, data_set_json)
                for data_set_id, data_set_json in self.connection_types[conn].target_data_sets.items():
                    data_sets_per_type[conn][auth][data_set_id] = self.generate_data_set_json(
                        conn, self.connection_types[conn].target_linked_service, data_set_json)

        return data_sets_per_type

    def create_connection_files(self):
        for _, linked_service_json in self.all_linked_services.items():
            self.write_linked_service_file(linked_service_json)
        
        for _, data_set_json in self.all_data_sets.items():
            self.write_data_set_file(data_set_json)

    def generate_pipelines(self, data_sets_per_type):
        for config in self.get_configs():
            for table_definition in config["tables"]:
                yield self.connection_types[config["connection"]](
                    config["name"], config["authentication"], 
                    config["config"], table_definition,
                    {
                        data_set_id: data_set_json["name"]
                        for data_set_id, data_set_json in data_sets_per_type[
                            config["connection"]][config["authentication"]].items()
                    }
                )
    
    def create_all(self):
        source_linked_services_by_type = self.find_required_linked_services()
        data_sets_per_type = \
            self.find_data_sets_per_type(source_linked_services_by_type)
        
        self.create_connection_files()

        for pipeline in self.generate_pipelines(data_sets_per_type):
            pipeline.generate_pipeline()
            self.write_pipeline_file(pipeline.pipeline_json)
