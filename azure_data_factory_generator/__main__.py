from os import path, makedirs
from sys import argv

from .initialise import CreateDataFactoryObjects

if __name__ == "__main__":
    if len(argv) < 3:
        raise Exception(
            "\n".join([
                "Need to pass the folder path where your config files are "
                "held, and to where the generated files should be placed",
                "Example: `python -m azure_data_factory_generator "
                "path/to/config/files/folder path/to/generated/files/folder`"
            ])
        )
    config_files_folder, generated_folder = argv[1], argv[2]

    if not path.exists(config_files_folder):
        raise Exception(
            f"Provided config files folder `{config_files_folder}`"
            " does not exist!")
    if not path.exists(generated_folder):
        makedirs(generated_folder)

    initialisation_obj = CreateDataFactoryObjects(
        config_files_folder, generated_folder)
    initialisation_obj.create_all()
