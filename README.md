# Ingenii Azure Data Factory Generator
Python based generator to create Azure Data Factory pipelines from configurations.

This package integrates easily with the [Ingenii Azure Data Platform](https://github.com/ingenii-solutions/azure-data-platform), but this package can be used independently as long as some required linked services and data sets are created ahead of time. These are detailed in the sections below.

* Current Version: 0.1.5

## Package installation

Install the package [using pip](https://pip.pypa.io/en/stable/user_guide/) with 
```
pip install ingeniiadfg
```
or, for a particular version
```
pip install ingeniiadfg==0.1.5
```
Alternatively, add it to your `requirements.txt` file. 

Use the package by calling it directly with the locations of your config files and the folder that the generated objects should be placed within:
```
python -m azure_data_factory_generator path/to/config/files/folder path/to/generated/files/folder
```

## Using the package

For details on using the package please refer to the [Azure Data Factory Usage documentation](docs/user/Usage.md). 

## Example CI/CD

For deploying into a Data Factory that is not integrated with a repository, also known as 'live' mode, we have included some example CI/CD pipelines in the `CICD` folder. These are in the format to be read by Azure Pipelines. Feel free to use these yourself or for inspiration in creating your own pipelines. 

## Version History

* `0.1.4`: Add object annotations to track what is managed by this package 
* `0.1.3`: Extend schedule to handle when only the hours of the dayt are specified 
* `0.1.2`: Change the name of the secret name for the SAS URI to access the config tables
* `0.1.1`: Add schedule generation from configuration, many more tests
* `0.1.0`: Initial package, FTP/SFTP connections with basic authentication
