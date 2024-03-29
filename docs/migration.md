# Migrating from Djinni

PyDjinni is heavily inspired by [Djinni](https://github.com/dropbox/djinni). The generated code is very similar to
the one generated by Djinni, and most of the support-library code is borrowed from the original implementation.

However, there are some major breaking changes that need to be considered when migrating to PyDjinni.

## Command Line Interface

The CLI has changed a lot. The preferred way of configuring the code generation process is now by specifying a
configuration file. This makes the CLI a lot more easy to use.

Consult the [Command Line Interface Reference](cli.md) for information on the new CLI, 
and the [Configuration Reference](config.md) for detailed documentation on all available configuration parameters.

## Interface Definition Language

The IDL has been slightly altered:

- Support for defining constants in records and interfaces has been removed.
- A new `function` type was introduced.
- The return type of methods is now indicated by an arrow (`->`) instead of a colon (`:`).
- Interface and record target languages are now defined with multi-letter indicators (`+cpp`, `+java`, `+objc`).

For all details of the PyDjinni IDL refer to the [Interface Definition Reference](idl.md).

## Support Library

The support library of PyDjinni is not compatible with the original support library in Djinni.
At the moment the changes in the interface are not significant, but it might diverge over time!

In PyDjinni, the support library is automatically copied to the generated code output alongside
the generated glue code by default. This means that there is no longer a need to include the library as a separate
target in the build process.

The new behaviour can be disabled if needed. As a fallback, the repository also provides CMake targets for each 
supported target language that can be included into the build manually.

## Processed files reporting

In Djinni, the list of input and output files could be reported to a file with the `--list-in-files` and 
`--list-out-files` arguments.
In PyDjinni, both reports are combined in a detailed _Processed Files_ report that can be generated in 
YAML, TOML or JSON file format.
It contains detailed information on all files that have been parsed and generated.

Consult the [Processed Files Reference](processed_files.md) for details on the new reporting format.

## External Types

The new file format for exporting and importing external types is incompatible to Djinni. Consult the [External Types Reference](external_types.md) for
detailed information on the new file format.
