def filter_for_files(output_activity):
    return {
        "name": f"Only files from {output_activity['name']}",
        "type": "Filter",
        "dependsOn": [
            {
                "activity": output_activity["name"],
                "dependencyConditions": [
                    "Succeeded"
                ]
            }
        ],
        "userProperties": [],
        "typeProperties": {
            "items": {
                "value": f"@activity('{output_activity['name']}').output.childItems",
                "type": "Expression"
            },
            "condition": {
                "value": "@equals(item().type, 'File')",
                "type": "Expression"
            }
        }
    }
