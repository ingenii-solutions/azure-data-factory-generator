# Ingenii Azure Data Factory Generator Usage

Here we detail how to use the [Ingenii Azure Data Factory Generator](https://github.com/ingenii-solutions/azure-data-factory-generator) to create the Azure Data Factory objects needed for your data obtaining pipelines.

This package will create `.json` files that will be then uploaded to your Azure Data Factory instance to define the objects it needs for your data obtaining pipelines. This package will generate definitions for:
1. self-hosted integration runtimes
2. linked services
3. datasets
4. pipelines
5. triggers

All the generated resources, with the exception of the integration runtimes where it is not possible, will have the annotation `ManagedByIngeniiADFG`, to help us manage the deployment, as detailed below. We recommend storing and maintaining your configuration files and these generated files in a git repository.

## Connections

Full details of the different connection sources we support, and how to set your configuration to connect to these sources can be found in the [Connections documentation](./Connections.md).

## Triggers

Full details of the triggers supported to schedule your pipelines can be found in the [Triggers documentation](./Triggers.md).

## Generation

A full example of how to structure your files in your own data engineering repository is given in the [Ingenii Azure Data Platform Data Engineering Example repository](https://github.com/ingenii-solutions/azure-data-platform-data-engineering-example), specifically in the [Pipeline Generation documentation](https://github.com/ingenii-solutions/azure-data-platform-data-engineering-example/blob/main/docs/user/Pipeline_Generation.md).

In short, all your config `.json` files should be contained in a folder, and a folder provided for the Data Factory `.json` files to be created into. These can both be the same folder.

In this package is a script to read your configuration files, aggregate to determine which objects are required, and then write out these objects in `.json` files to be uploaded. The command has the structure

```
<python executable name> -m azure_data_factory_generator <folder that config .json files are held> <folder that the generated files should be added to>
```

So, if your configuration files are in a folder called `pipeline_generation`, you can run the command

```
python -m azure_data_factory_generator pipeline_generation pipeline_generation
```

This will read all the `.json` files it finds in the folder - it will not traverse into subfolders - and then add the generated objects into subfolders called `dataset`, `integrationruntime`, etc. These can then be committed to your git repository.

## Deployment

### Approach

[Azure does have recommendations and guides](https://docs.microsoft.com/en-us/azure/data-factory/continuous-integration-delivery) of how to deploy to a Data Factory, the `CD` part of `CI/CD`. We take a different approach for two reasons:

1. Their apporoach involves developing the resources in a development Data Factory, where we are creating these through this Python package
2. The approach of using an ARM template will define the entire Factory, while in our approach you can add other resources to your Data Factory directly, and this package will only manage the sub-set they create.

### Tools

1. [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/) to compare the current state of your Data Factory and update the resources as required. Details of how to install the `az` tool [can be found here](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli).
2. [jq](https://stedolan.github.io/jq/) to read and extract information from the generated `.json` files.

### Deployment Scripts

Example scripts to deploy the resources and remove anything in the Data Factory no longer needed are in the `deployment` folder of [this repository](https://github.com/ingenii-solutions/azure-data-factory-generator). You can use these for your own scripts, or please refer to the CI/CD pipeline for Azure DevOps we detail in the [Ingenii Azure Data Platform Data Engineering Example repository](https://github.com/ingenii-solutions/azure-data-platform-data-engineering-example).

1. `add_objects.sh`: Deploys the resources, overwriting anything with the same name in the Data Factory already. The deployments must happen in this order as objects refer to each other; for example data sets expect the linked service to already exist, otherwise the deployment will fail.
2. `clean_objects.sh`: Looks to remove any resources that the package once generated, but are now no longer used. Removes any resources with the annotation `ManagedByIngeniiADFG` which is in the Data Factory but not in the configuration. If there's a resource that you want to keep because you're using it in other pipelines, then you can remove the annotation to stop this behaviour. The exception is integration runtimes, which can't be annotated or removed using the CLI.
