# CMake

PyDjinni comes with a CMake module that allows for easy integration of the interface generation
in a CMake project configuration.

## Synopsis

```cmake
pydjinni_generate(<filename>
    LANGUAGES <{{ supported_targets() }}> [{{ supported_targets() }} ...]
    [CONFIG <config>]
    [OPTIONS <options>]
    [WORKING_DIRECTORY <workdir>]
)
```

Calls the PyDjinni Generator and populates variables with the generated sources

The output variables are named `<language>_GENERATED_SOURCES`, `<language>_GENERATED_HEADERS` and 
`<language>_INCLUDE_DIR`, where `<language>` refers to the *Generator* language.

Sets the `CMAKE_CONFIGURE_DEPENDS` property on all reported input files (parsed IDL files, external types that are 
picked up during parsing and the used config file), to automatically trigger re-configuration when one of the 
referenced files changes.

In case of an error, the CMake configuration is aborted.

## Options

The options are:

* `<filename>`<br>Filename/path of the Djinni-IDL file that should be processed.
* `LANGUAGES`<br>List of languages that bindings should be generated for. 
  Possible values: {{ supported_targets(", ", "`") }}.
* `CONFIG <config>` *Optional*<br>Filename/path to the configuration file. Defaults to `pydjinni.yaml`. To disable the
  configuration with a config file completely, set `CONFIG` to `None`.
* `OPTIONS <options>` *Optional*<br>List of additional arbitrary configuration options that should be passed to the CLI.
* `WORKING_DIRECTORY <workdir>` *Optional*<br>The working-directory from which the generate command should be executed.
  <br>Default: `CMAKE_CURRENT_SOURCE_DIR`.

## Installation

### Find Package

The CMake module is distributed with the Pydjinni Python package.
It can be discovered automatically in the current Python environment with this `FindPyDjinni` module:

[:octicons-download-16: FindPyDjinni.cmake](https://raw.githubusercontent.com/pydjinni/pydjinni/{{ git.tag }}/src/pydjinni/cmake/modules/FindPyDjinni.cmake){ .md-button download="FindPyDjinni.cmake" }

```cmake
list(APPEND CMAKE_MODULE_PATH 
    # directory that contains FindPyDjinni.cmake
    ${CMAKE_SOURCE_DIR}/cmake/modules) 
find_package(PyDjinni)
include(PyDjinni)

```

Using `find_package()` has the advantage that the included CMake module is guaranteed to be compatible with the currently installed version of PyDjinni.

### Manual Copy

The module can also be manually copied into the project:

[:octicons-download-16: PyDjinni.cmake {{ git.tag }}](https://raw.githubusercontent.com/pydjinni/pydjinni/{{ git.tag }}/src/pydjinni/cmake/modules/PyDjinni.cmake){ .md-button download="PyDjinni.cmake" }

```cmake
list(APPEND CMAKE_MODULE_PATH 
    # directory that contains PyDjinni.cmake
    ${CMAKE_SOURCE_DIR}/cmake)
include(Pydjinni)
```

The disadvantage of this approach is that the module may need to be updated manually if it becomes incompatible with PyDjinni after an update.

## Example

```cmake
pydjinni_generate(example.pydjinni
    LANGUAGES java
    OPTIONS
        generate.java.out=out/java
        generate.java.package=foo.bar.package
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
)
```

This will call `pydjinni generate example.djinni java` in the top level of the current CMake source tree.

The following variables are populated:

- `java_GENERATED_SOURCES`
- `jni_GENERATED_SOURCES`
- `jni_GENERATED_HEADERS`
- `jni_INCLUDE_DIR`

