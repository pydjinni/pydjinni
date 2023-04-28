# Configuration Reference

PyDjinni can be configured in three different ways:

1. The preferred way is to provide a configuration file in the provided Schema, that holds all the configuration information.
   If the file is named `pydjinni.yaml`, it is picked up automatically. With the parameter `--config` a custom filename
   can be specified. The type of the file is determined by the filename extension.
   <br>Supported extensions are: `.yaml`, `.yml`, `.json`, `.toml`
   <br>**Example**: `pydjinni --config=custom_filename.yaml generate input.djinni cpp`
2. The CLI also provides the `--option` parameter, that allows to set one or more configuration keys.
   If a key is already specified in the configuration file, it will be overridden by this parameter.
   <br>**Example**: `pydjinni --option generate.cpp.out:cpp_out_path generate input.djinni cpp`
3. Options can also be provided by setting the `PYDJINNI_OPTION` environment variable. Multiple options can be provided
   by setting a string of space separated options to the variable.
   <br>**Example**: `PYDJINNI_OPTION="generate.cpp.out.header:header_out generate.cpp.out.source:src_out"`


## Configuration options

[:material-file-document-check-outline: JSON-Schema](/json-schema/config_schema.json){ .md-button target="_blank" }

{{ config_schema_table() }}

## Type definitions

### OutPaths

{{ config_schema_definition("OutPaths") }}

### IdentifierStyle

{{ config_schema_definition("IdentifierStyle") }}
