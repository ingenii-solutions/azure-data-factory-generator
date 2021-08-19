default_policy = {
    "timeout": "0.00:01:00",
    "retry": 3,
    "retryIntervalInSeconds": 30,
    "secureOutput": False,
    "secureInput": False
}


class DataFactoryPipeline:
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
