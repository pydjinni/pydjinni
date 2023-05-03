# CMake

PyDjinni comes with a CMake module that allows for easy integration of the interface generation
in the CMake configuration step.

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

The output variables are named `<language>_GENERATED_SOURCES` and `<language>_GENERATED_HEADERS`, where `<language>`
refers to the *Generator* language.

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
* `WORKING_DIRECTORY <workdir>` *Optional*<br>The working-directory from which the generate comment should be executed.
  <br>Default: `CMAKE_CURRENT_SOURCE_DIR`.

## Installation

### FetchContent

The recommended installation approach is by using `FetchContent`.
Make sure to call `FetchContent_MakeAvailable` [before the first `project` declaration](https://cmake.org/cmake/help/latest/module/FetchContent.html#populating-content-without-adding-it-to-the-build){ target="_blank" } in your `CMakeLists.txt`:

```cmake
cmake_minimum_required(VERSION 3.14)

include(FetchContent)
FetchContent_Declare(
  pydjinni
  GIT_TAG v1.0.0 # or any later version
  URL  https://github.com/pydjinni/pydjinni
  SOURCE_DIR cmake
)
FetchContent_MakeAvailable(pydjinni)

list(APPEND CMAKE_MODULE_PATH ${pydjinni_SOURCE_DIR})

include(PyDjinni)

project(CrossCompileExample)
```

### Manual Copy

If you don't want to check out the entire project just to use the CMake module, the file can also be copied into the 
project manually, and just included from the path were it was copied to:

```cmake
list(APPEND CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/cmake)
include(Pydjinni)
```

[:octicons-download-16: Download PyDjinni Module](https://raw.githubusercontent.com/pydjinni/pydjinni/{{ git.tag }}/cmake/modules/PyDjinni.cmake){ .md-button download }


## Example

```cmake
pydjinni_generate(example.djinni
    LANGUAGES java
    OPTIONS
        generate.java.out:out/java
        generate.java.package:foo.bar.package
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
)
```

This will call `pydjinni generate example.djinni java` in the top level of the current CMake source tree.

The following variables are populated:

- `java_GENERATED_SOURCES`
- `jni_GENERATED_SOURCES`
- `jni_GENERATED_HEADERS`

