# Introduction

PyDjinni is a toolchain that supports the process of developing, building, packaging and publishing a cross-platform 
library written in C++.

## Interface Definition

The PyDjinni Interface Definition Language (IDL) is used to define the language interoperability interfaces between
C++ and a target programming language like Java, Objective-C or Swift.

From the IDL, glue code is generated that automatically converts data and delegates
method calls across the language boundary.

Consult the [Interface Definition](idl.md) Reference for a full documentation of all features of the IDL.

```djinni
my_cool_enum = enum {
    option1;
    option2;
    option3;
}

# test comment
# this is a test comment with a list:
# * first
# * second
my_flags = flags {
    # flag comment
    flag1;
    flag2;
    flag3;
    no_flags = none;
    all_flags = all;
    more = all;
}

foo = record {
    # comment
    id: i16;
    info: i16;
}

my_cpp_interface = main interface +cpp {
    # comment
    method_returning_nothing(
        value: i16,
        foo: i16
    );
    method_returning_some_type(key: i8) -> foo;
    static get_version() -> i8;
}
```


## Generating Interfaces

The `generate` subcommand produces glue code in the specified target languages from the PyDjinni IDL.

The following command generates Java and C++ language bindings for Android from the `foo.pydjinni` IDL file:

```bash
pydjinni generate foo.pydjinni cpp java
```

## Building and Packaging { .new-badge }

PyDjinni does also come with tools supporting the building and packaging process of a cross-platform C++ library.

The `package` subcommand builds and packages distributable artifacts for the specified platforms.

The following commands produce both an Android Archive (AAR) and Swift package for iOS and macOS:

```
pydjinni package aar android
pydjinni package swiftpackage ios macos ios_simulator
```

## Publishing { .new-badge }

Once artifacts are built, they can be published easily with PyDjinni.

It can upload the distribution artifact to a repository or registry, hiding away the underlying process that is 
different for every targeted platform:

```shell
pydjinni publish aar
pydjinni publish swiftpackage
```

## Configuration

All details of generating glue code and building, packaging and publishing a cross-platform library with PyDjinni is
configured through the `pydjinni.yaml` configuration file.

For a full overview of all available configuration parameters, consult the [Configuration Reference](config.md).

The following example shows what a minimal configuration file could look like:

```yaml
generate:
  cpp:
    out:
      header: generated/cpp/include
      source: generated/cpp/src
    namespace: pydjinni::example
  java:
    out: lib/generated/java
    package: com.pydjinni.example
  jni:
    out: lib/generated/jni
  objc:
    out: lib/generated/objc
  objcpp:
    out: generated/objcpp
    namespace: pydjinni::example::objcpp
    swift:
      bridging_header: PyDjinniLibrary.h
package:
  version: 1.1.0
  target: MyLibrary
  swiftpackage:
    publish:
      repository: github.com/foo/bar.git
    platforms:
      ios: [armv8]
      ios_simulator: [x86_64, armv8]
  aar:
    publish:
      group_id: com.pydjinni
      artifact_id: example
      maven_registry: https://maven.pkg.github.com/foo/bar
    platforms:
      android: [x86_64, armv8]
```

### Credentials

Credentials for artifact publication should not be stored in the configuration file or passed to the command via the CLI.
Instead, they can be set as environment variables or in a `.env` file:

```sh
pydjinni__package__aar__publish__username=foo
pydjinni__package__aar__publish__password=<password>
pydjinni__package__swiftpackage__publish__username=bar
pydjinni__package__swiftpackage__publish__password=<password>
```
