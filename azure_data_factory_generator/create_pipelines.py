import json

from api import generate_api_pipeline
from sftp import generate_sftp_pipeline

with open("scratch/sftp_config.json", "r") as pipeline_file:
    full_config = json.load(pipeline_file)

if full_config["connection"] == "api":
    generate_pipeline_function = generate_api_pipeline
elif full_config["connection"] == "sftp":
    generate_pipeline_function = generate_sftp_pipeline
else:
    raise Exception(f"Don't recognise connection type {full_config['connection']}!")

for table in full_config["tables"]:
    pipeline = generate_pipeline_function(full_config["name"], full_config["config"], table)

    with open(f"scratch/{pipeline.pipeline_json['name']}.json", "w") as pipeline_file:
        json.dump(pipeline.pipeline_json, pipeline_file, indent=4)
