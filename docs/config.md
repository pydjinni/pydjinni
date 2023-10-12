# Configuration Reference

PyDjinni can be configured in different ways:

- **Configuration file**: If a file named `pydjinni.yaml` exists, it is picked up automatically. 
  With the parameter `--config` a custom filename can be specified.
  The type of the file is determined by the filename extension.
  <br>Supported extensions are: `.yaml`, `.yml`, `.json`, `.toml`
  <br>**Example**: `pydjinni --config=custom_filename.yaml generate input.djinni cpp`
- **CLI**: The CLI `--option` parameter allows to set one or more configuration keys.
  Values from the configuration file can be overridden by commandline parameters.
  <br>**Example**: `pydjinni --option generate.cpp.out=cpp_out_path generate input.djinni cpp`
- **Environment Variables**: Options can also be provided by setting environment variables.
  Environment variables can also be set in a `.env` file.
  The file is automatically detected if present in the working directory.
  <br>**Example**: the environment variable `pydjinni__generate__cpp__out=header_out` is the equivalent to 
                    passing `--option generate.cpp.out` to the CLI.
- For some common settings a shortcut in the form of a special argument is provided by the CLI. 
  <br>**Example**: When packaging a library, the default build configuration can be overridden like so:
  `pydjinni package --configuration Debug aar android`. The `--configuration` argument is equivalent to setting the
  `package.configuration` value in the configuration file or to passing the argument `-o package.configuration=Debug`
  to the CLI.

## Configuration Parameters

[:material-file-document-check-outline: JSON-Schema](/json-schema/config_schema.json){ .md-button target="_blank" }

{{ config_schema_table() }}

## Type Definitions

### OutPaths

{{ config_schema_definition("OutPaths") }}

### IdentifierStyle

{{ config_schema_definition("IdentifierStyle") }}
