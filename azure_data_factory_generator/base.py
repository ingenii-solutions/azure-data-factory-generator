from abc import ABC, abstractmethod
from typing import List

class DataFactoryPipeline(ABC):
    
    # The general name of the connection type
    name = None

    # Dictionary where the keys are the names of the possible authentication
    # options e.g. 'basic', 'token'. The values are a sub-dictionary with 2
    # keys, 'required', and 'optional', and those values are a list of the
    # corresponding parameters required or optional for this connection type
    authentications = {}

    # A list of strings giving the names of the required and optional
    # parameters to define for each table
    required_table_parameters = []
    optional_table_parameters = []

    default_policy = {
        "timeout": "0.00:01:00",
        "retry": 3,
        "retryIntervalInSeconds": 30,
        "secureOutput": False,
        "secureInput": False
    }

    @classmethod
    def is_valid_authentication(cls, authentication_method: str) -> bool:
        return authentication_method in cls.authentications

    @classmethod
    def all_authentications(cls) -> List[str]:
        return list(cls.authentications.keys())

    @staticmethod
    def _validate_config(config: dict, required_parameters: List[str],
                         optional_parameters: List[str]) -> None:
        """
        Validate any config given the lists of parameters
        """
        errors = []

        missing_parameters = [
            rp for rp in required_parameters
            if rp not in config
        ]
        if missing_parameters:
            errors.append(f"Fields missing from config: {missing_parameters}")

        unknown_parameters = [
            c for c in config
            if c not in required_parameters + optional_parameters
        ]
        if unknown_parameters:
            errors.append(f"Unknown fields in config: {unknown_parameters}")

        if errors:
            raise Exception(errors)

    def __init__(self, name):
        self.pipeline_json = {
            "name": name,
            "properties": {
                "activities": [],
                "parameters": {},
                "variables": {},
                "annotations": []
            }
        }

    def add_activity(self, activity_json, depends_on=[]):
        self.pipeline_json["properties"]["activities"].append({
            **activity_json, 
            "dependsOn": [
                {
                    "activity": activity["name"],
                    "dependencyConditions": ["Succeeded"]
                }
                for activity in depends_on
                ]
            })

    @abstractmethod
    def generate_pipeline(self):
        ...
