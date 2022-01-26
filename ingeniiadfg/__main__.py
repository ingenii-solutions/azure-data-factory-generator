from os import path, makedirs
import typer

from .initialise import CreateDataFactoryObjects

app = typer.Typer()
app(prog_name="ingeniiadfg")

def generate_objects(
    config_folder: str, target_folder: str = ".",
    remove_non_generated: bool = False
        ):

    # if len(argv) < 3:
    #     raise Exception(
    #         "\n".join([
    #             "Need to pass the folder path where your config files are "
    #             "held, and to where the generated files should be placed",
    #             "Example: `python -m azure_data_factory_generator "
    #             "path/to/config/files/folder path/to/generated/files/folder`"
    #         ])
    #     )

    if not path.exists(config_folder):
        raise Exception(
            f"Provided config files folder `{config_folder}`"
            " does not exist!")
    if target_folder != "." and not path.exists(target_folder):
        makedirs(target_folder)

    initialisation_obj = CreateDataFactoryObjects(
        config_folder, target_folder)
    initialisation_obj.create_all(remove_non_generated=remove_non_generated)

if __name__ == "__main__":
    typer.run(generate_objects)
