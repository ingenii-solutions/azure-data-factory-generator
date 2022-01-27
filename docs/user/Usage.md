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

A full example of how to structure your files in your own Data Factory repository is given in the [Ingenii Azure Data Factory Initial Repository](https://github.com/ingenii-solutions/azure-data-factory-initial-repository).

In this package is a script that reads your configuration files, aggregates to determine which objects are required, and then writes out these objects in `.json` files for the Data Factory to use. The command has the structure

```
ingeniiadfg generate <folder that config .json files are held> <optional: folder that the generated files should be added to>
```

So, if your configuration files are in a folder called `adfg_configs`, you can run the command

```
ingeniiadfg generate adfg_configs
```

This will read all the `.json` files it finds in the `adfg_configs` folder - it will not traverse into subfolders - and then add the generated objects into subfolders called `dataset`, `integrationruntime`, etc., at the folder that the command is run in which should be the root of your repository. These files can then be committed to your git repository to be used byt eh Data Factory.

## Deployment

### Approach

[Azure has recommendations and guides](https://docs.microsoft.com/en-us/azure/data-factory/continuous-integration-delivery) of how to deploy to a Data Factory, the `CD` part of `CI/CD`. Please see our example CI/CD pipelines on the [`adf_publish` branch of the Ingenii Azure Data Factory Initial Repository](https://github.com/ingenii-solutions/azure-data-factory-initial-repository/tree/adf_publish).

### Deployment Scripts

If for whatever reason you're not integrating your Data Factory with a repository - also known as `live` mode - we have some example scripts and pipelines in the `CICD` and `deployment` folders. Feel free to use these as the basis of your own approach.

1. `add_objects.sh`: Deploys the resources, overwriting anything with the same name in the Data Factory already. The deployments must happen in this order as objects refer to each other; for example data sets expect the linked service to already exist, otherwise the deployment will fail.
2. `clean_objects.sh`: Looks to remove any resources that the package once generated, but are now no longer used. Removes any resources with the annotation `ManagedByIngeniiADFG` which is in the Data Factory but not in the configuration. If there's a resource that you want to keep because you're using it in other pipelines, then you can remove the annotation to stop this behaviour. The exception is integration runtimes, which can't be annotated or removed using the CLI.
