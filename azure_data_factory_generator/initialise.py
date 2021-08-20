import json
from os import listdir, mkdir, path

from sftp import SFTPPipeline

config_folder = "example_configs"
generated_folder = "generated"
data_set_folder = f"{generated_folder}/dataset"
if not path.exists(data_set_folder):
    mkdir(data_set_folder)

connection_types = {
    "sftp": SFTPPipeline
}

# all_configs = listdir(config_folder)
# Pretend this is all configs
all_configs = ["sftp_basic.json"]

# Find all types
raw_configs = []
types = {}
for config_file_name in all_configs:
    with open(f"{config_folder}/{config_file_name}", "r") as json_file:
        config = json.load(json_file)
    
    raw_configs.append(config)

    connection, authentication = \
        config["config"]["connection"], config["config"]["authentication"]
    types[connection] = \
        types.get(connection, set()) | set([authentication])

# Validation of configs

# Determine required linked services and data sets
linked_services = {
    conn: {
        auth: connection_types[conn].authentications[auth]["linked_service"]
        for auth in auths
    }
    for conn, auths in types.items()
}

## Get the linked service parameters
for conn, auths in linked_services.items():
    for auth, linked_service_json in auths.items():
        
        for data_set_json in connection_types[conn].source_data_sets:
            
            ds_name = data_set_json["name"]
            if ds_name.lower().startswith(conn.lower()):
                ds_name = ds_name[len(conn):]
            
            data_set_json["name"] = linked_service_json["name"] + ds_name

            # Add linked service definition, uncluding required parameters
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
            
            # Output dataset
            with open(f"{data_set_folder}/{data_set_json['name']}.json", "w") as generated_dataset:
                json.dump(data_set_json, generated_dataset, indent=4)
