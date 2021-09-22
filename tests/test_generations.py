from azure_data_factory_generator.initialise import CreateDataFactoryObjects
from deepdiff import DeepDiff
import json
import os
import unittest


class ExampleConfigGenerations(unittest.TestCase):

    test_folders = []
    errors = []
    comparison_files = {}

    def setUp(self):
        # Find test folders
        for top_level in os.listdir("tests"):
            if not os.path.isdir(f"tests/{top_level}"):
                continue
            if top_level.startswith("__"):
                continue
            self.test_folders.append(top_level)

    @staticmethod
    def load_json(json_path):
        with open(json_path) as json_file:
            return json.load(json_file)

    def check_all_files_created_by_type(
            self, test_name, file_type, generated_file_names):
        self.comparison_files[test_name][file_type] = []
        expected_file_names = [
            file.replace(".json", "")
            for file in os.listdir(f"tests/{test_name}/expected/{file_type}")
        ]
        for dsn in expected_file_names:
            if dsn not in generated_file_names:
                self.errors.append({
                    "test": test_name,
                    "type": "missing_file",
                    "message": f"{file_type} {dsn} expected but not created"
                })
        for dsn in generated_file_names:
            if dsn not in expected_file_names:
                self.errors.append({
                    "test": test_name,
                    "type": "extra_file",
                    "message": f"{file_type} {dsn} created but not expected"
                })
            else:
                self.comparison_files[test_name][file_type].append(dsn)

    def check_all_files_created(self, test_name, init_obj):
        self.comparison_files[test_name] = {}
        self.check_all_files_created_by_type(
            test_name, "integrationRuntime", {
                integration_runtime["name"]: integration_runtime
                for _, integration_runtime
                in init_obj.all_self_hosted_integration_runtimes.items()}
        )
        self.check_all_files_created_by_type(
            test_name, "linkedService", [
                linked_service["name"]
                for _, linked_service
                in init_obj.all_linked_service_jsons.items()]
        )
        self.check_all_files_created_by_type(
            test_name, "dataset", [
                data_set["name"]
                for _, data_set in init_obj.all_data_set_jsons.items()]
        )
        self.check_all_files_created_by_type(
            test_name, "pipeline", [
                pipeline["name"]
                for _, pipeline in init_obj.all_pipelines.items()]
        )
        self.check_all_files_created_by_type(
            test_name, "trigger", {
                trigger["name"]: trigger
                for _, trigger in init_obj.all_trigger_jsons.items()}
        )

    def handle_deepdiff_comparison(
                self, test_name, file_type, expected_file_name, comparison):
        for dd_type, message in comparison.items():
            if dd_type == "dictionary_item_added":
                self.errors.append({
                    "test": test_name,
                    "type": "extra_item_in_generated_file",
                    "message": f"{file_type} {expected_file_name} "
                               f"has a extra entries in the generated version:"
                               f" {message}"
                })
            elif dd_type == "dictionary_item_removed":
                self.errors.append({
                    "test": test_name,
                    "type": "removed_item_in_generated_file",
                    "message": f"{file_type} {expected_file_name} "
                               f"has missing entries in the generated version:"
                               f" {message}"
                })
            elif dd_type == "values_changed":
                self.errors.append({
                    "test": test_name,
                    "type": "different_value_in_generated_file",
                    "message": f"{file_type} {expected_file_name} has a "
                               f"different value: {message}"
                })
            elif dd_type == "type_changes":
                self.errors.append({
                    "test": test_name,
                    "type": "type_change_in_generated_file",
                    "message": f"{file_type} {expected_file_name} has a value "
                               f"with a different type: {message}"
                })
            elif dd_type == "iterable_item_added":
                self.errors.append({
                    "test": test_name,
                    "type": "extra_item_in_list_in_generated_file",
                    "message": f"{file_type} {expected_file_name} has extra "
                               f"entries in a list: {message}"
                })
            elif dd_type == "iterable_item_removed":
                self.errors.append({
                    "test": test_name,
                    "type": "missing_item_in_list_in_generated_file",
                    "message": f"{file_type} {expected_file_name} is missing "
                               f"entries from a list: {message}"
                })
            else:
                self.errors.append({
                    "test": test_name,
                    "type": "other_error_in_file_comparison",
                    "message": f"{file_type} {expected_file_name} has an "
                               f"error: {dd_type}, {message}"
                })

    def compare_files_by_type(self, test_name, file_type, generated_files):
        for expected_file_name in self.comparison_files[test_name][file_type]:

            expected_json = self.load_json(
                f"tests/{test_name}/expected/"
                f"{file_type}/{expected_file_name}.json")
            generated_json = generated_files[expected_file_name]

            comparison = DeepDiff(expected_json, generated_json)
            if comparison:
                self.handle_deepdiff_comparison(
                    test_name, file_type, expected_file_name, comparison)

    def compare_files(self, test_name, init_obj):
        self.compare_files_by_type(
            test_name, "integrationRuntime", {
                integration_runtime["name"]: integration_runtime
                for _, integration_runtime
                in init_obj.all_self_hosted_integration_runtimes.items()}
        )
        self.compare_files_by_type(
            test_name, "linkedService", {
                linked_service["name"]: linked_service
                for _, linked_service
                in init_obj.all_linked_service_jsons.items()}
        )
        self.compare_files_by_type(
            test_name, "dataset", {
                data_set["name"]: data_set
                for _, data_set in init_obj.all_data_set_jsons.items()}
        )
        self.compare_files_by_type(
            test_name, "pipeline", {
                pipeline["name"]: pipeline
                for _, pipeline in init_obj.all_pipelines.items()}
        )
        self.compare_files_by_type(
            test_name, "trigger", {
                trigger["name"]: trigger
                for _, trigger in init_obj.all_trigger_jsons.items()}
        )

    def test_everything(self):
        for test_name in self.test_folders:

            initialisation_obj = CreateDataFactoryObjects(
                f"tests/{test_name}/config",
                f"tests/{test_name}/generated")
            initialisation_obj.create_all_jsons()

            self.check_all_files_created(test_name, initialisation_obj)
            self.compare_files(test_name, initialisation_obj)

        self.assertListEqual([], self.errors)
