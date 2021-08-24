from copy import deepcopy
import json
from os import listdir, makedirs, path

from .sftp import SFTPPipeline
from .templates.dataset import all_data_sets
from .templates.linked_service import all_linked_services

class CreateDataFactoryObjects:

    connection_types = {
        "sftp": SFTPPipeline
    }

    all_source_connections = set()
    all_target_connections = set()

    all_linked_services = set()
    all_data_sets = set()

    all_config_jsons = []
    all_self_hosted_integration_runtimes = {}
    all_linked_service_jsons = {}
    all_data_set_jsons = {}
    all_pipelines = {}

    source_data_sets_per_type = {}
    target_data_sets = {}

    base_integration_runtime = "AutoResolveIntegrationRuntime"

    def __init__(self, config_folder=None, generated_folder=None):
        self.config_folder = config_folder or "configs"
        self.generated_folder = generated_folder or "generated"

        self.shir_folder = f"{self.generated_folder}/integrationRuntime"
        self.linked_service_folder = f"{self.generated_folder}/linkedService"
        self.data_set_folder = f"{self.generated_folder}/dataset"
        self.pipeline_folder = f"{self.generated_folder}/pipeline"

        self.check_folders()

    def check_folders(self):
        for folder in [
                self.shir_folder, self.linked_service_folder, 
                self.data_set_folder, self.pipeline_folder
            ]:
            if not path.exists(folder):
                makedirs(folder)

    def get_configs(self):
        if not self.all_config_jsons:
            for config_file_name in listdir(self.config_folder):

                if not config_file_name.endswith(".json"):
                    continue

                with open(f"{self.config_folder}/{config_file_name}", "r") as json_file:
                    self.all_config_jsons.append(json.load(json_file))

        for config_json in self.all_config_jsons:
            yield config_json

    def find_self_hosted_integration_runtimes(self):
        for config in self.get_configs():
            if "self_hosted_integration_runtime" in config:
                shir_name = config["self_hosted_integration_runtime"]
                if shir_name not in self.all_self_hosted_integration_runtimes:
                    self.all_self_hosted_integration_runtimes[shir_name] = {
                        "name": shir_name,
                        "properties": {
                            "type": "SelfHosted"
                            }
                    }

    def find_all_connections(self):
        # Find all unique instances of connection and authentication types

        if not self.all_linked_services:
            for config in self.get_configs():
                conn = config["connection"]
                auth = config["authentication"]
                ir_name = config.get(
                    "self_hosted_integration_runtime", 
                    self.base_integration_runtime)
                
                source_ls = \
                    self.connection_types[conn] \
                        .authentications[auth]["linked_service"]["name"]
                self.all_linked_services.add(
                    (source_ls, ir_name))

                for _, source_dataset in self.connection_types[conn].source_data_sets.items():
                    self.all_data_sets.add(
                        (source_ls, ir_name, source_dataset["name"]))
                
                target_ls = \
                    self.connection_types[conn].target_linked_service["name"]
                self.all_linked_services.add(
                    (target_ls, ir_name))

                for _, target_dataset in self.connection_types[conn].target_data_sets.items():
                    self.all_data_sets.add(
                        (target_ls, ir_name, target_dataset["name"]))
                
        # Validation of configs

    def create_linked_service_name(self, base_name, integration_runtime_name):
        if integration_runtime_name == self.base_integration_runtime:
            return base_name
        else:
            return f"{base_name}{integration_runtime_name}"

    def create_linked_service(self, base_json, integration_runtime_name):
        if integration_runtime_name == self.base_integration_runtime:
            return base_json
        else:
            new_linked_service = deepcopy(base_json)
            new_linked_service["name"] = \
                self.create_linked_service_name(base_json["name"], 
                                                integration_runtime_name)
            new_linked_service["properties"]["connectVia"] = {
			    "referenceName": integration_runtime_name,
			    "type": "IntegrationRuntimeReference"
		    }
            return new_linked_service

    def find_all_linked_services(self):
        # Find only the required linked services
        self.find_all_connections()

        for ls_name, ir_name in self.all_linked_services:

            template_linked_service = all_linked_services[ls_name]
            
            ls_json = self.create_linked_service(template_linked_service, ir_name)
            if ls_json["name"] not in self.all_linked_service_jsons:
                self.all_linked_service_jsons[ls_json["name"]] = ls_json

    def find_all_data_sets(self):
        for ls_name, ir_name, ds_name in self.all_data_sets:

            linked_service_json = self.all_linked_service_jsons[
                    self.create_linked_service_name(
                        ls_name, ir_name)
                ]
            data_set_template = all_data_sets[ds_name]

            ds_id = (linked_service_json["name"], data_set_template["name"])
            if ds_id not in self.all_data_set_jsons:

                data_set_json = deepcopy(data_set_template)

                ds_name = data_set_json["name"]
                if ds_name.lower().startswith(linked_service_json["name"].lower()):
                    ds_name = ds_name[len(linked_service_json["name"]):]
                
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
                
                self.all_data_set_jsons[ds_id] = data_set_json

    def generate_pipelines(self):

        for config in self.get_configs():
            conn = config["connection"]
            auth = config["authentication"]
            ir_name = config.get(
                "self_hosted_integration_runtime", 
                self.base_integration_runtime)

            pipeline_class = self.connection_types[conn]

            source_linked_service_name = self.create_linked_service_name(
                pipeline_class.authentications[auth]["linked_service"]["name"], ir_name)
            target_linked_service_name = self.create_linked_service_name(
                pipeline_class.target_linked_service["name"], ir_name)

            pipeline_datasets = {
                **{
                    data_set_id: self.all_data_set_jsons[(source_linked_service_name, data_set_template["name"])]
                    for data_set_id, data_set_template in pipeline_class.source_data_sets.items()
                },
                **{
                    data_set_id: self.all_data_set_jsons[(target_linked_service_name, data_set_template["name"])]
                    for data_set_id, data_set_template in pipeline_class.target_data_sets.items()
                }
            }

            for table_definition in config["tables"]:
                pipeline_obj = pipeline_class(
                    config["name"], config["authentication"], 
                    config["config"], table_definition, pipeline_datasets
                )
                pipeline_obj.generate_pipeline()
                self.all_pipelines[pipeline_obj.pipeline_json["name"]] = \
                    pipeline_obj.pipeline_json
    
    def create_all_jsons(self):
        self.find_self_hosted_integration_runtimes()
        self.find_all_linked_services()
        self.find_all_data_sets()
        self.generate_pipelines()
        
    def write_json(self, file_path, json_to_write):
        with open(file_path, "w") as json_file:
            json.dump(json_to_write, json_file, indent=4)

    def create_all(self):
        self.create_all_jsons()
        
        for _, shir_json in self.all_self_hosted_integration_runtimes.items():
            self.write_json(
                f"{self.shir_folder}/{shir_json['name']}.json",
                shir_json
            )
        for _, linked_service_json in self.all_linked_service_jsons.items():
            self.write_json(
                f"{self.linked_service_folder}/{linked_service_json['name']}.json",
                linked_service_json
            )
        for _, data_set_json in self.all_data_set_jsons.items():
            self.write_json(
                f"{self.data_set_folder}/{data_set_json['name']}.json",
                data_set_json
            )
        for _, pipeline_json in self.all_pipelines.items():
            self.write_json(
                f"{self.pipeline_folder}/{pipeline_json['name']}.json",
                pipeline_json
            )
