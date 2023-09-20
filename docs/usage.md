# Usage

PyDjinni aims to support the full development process of a cross-language
library written in C++. It does so by making a lot of opinionated presumptions along the way.

It also comes with a flexible plugin system that allows to adapt certain behaviour to the needs of your own requirements.

If the development process provided does not fit your needs nevertheless, it is still possible to
just use the `pydjinni generate` command set and ignore all the other tools in the swiss knife.

## Generate

Generate java language bindings for android from the `foo.djinni` IDL file:

```bash
pydjinni generate foo.djinni java
```

Generate objc bindings with custom config:

```bash
pydinni generate --config=.pydjinni.yaml foo.djinni objc
```

## Build and Package

Build for a variety of target platforms and package the results for distribution:

```
pydjinni package aar android
pydjinni package swiftpackage ios macos ios_simulator
```

## Publish

Upload the distribution artifact to a repository or registry:

```shell
pydjinni publish aar
pydjinni publish swiftpackage
```


## Config file

```yaml
  generate:
    java:
      out: lib/djinni-generated/java
      package: pro.jothe.test
    jni:
      out: lib/djinni-generated/jni
    objc:
      out: lib/djinni-generated/objc
  build:
    conan:
      profiles: profiles
  package:
    out: dist
    build_strategy: conan
    version: 1.1.0
    configuration: Debug
    target: MyLibrary
    swiftpackage:
      publish:
        repository: gitlab.com/jothepro/foo.git
        branch: main
      platforms:
          macos: [armv8]
          ios: [armv8]
          ios_simulator: [x86_64, armv8]
    aar:
      publish:
          group_id: foo.bar
          artifact_id: baz
          url: https://maven.pkg.github.com/foo/bar
      platforms:
          android: [x86_64, armv8]
```

## Credentials

Credentials for artifact publication should not be stored in the configuration file or passed to the command via the CLI.
Instead, they can be set as environment variables or in a `.env` file:

```sh
pydjinni__package__aar__publish__username=foo
pydjinni__package__aar__publish__password=<password>
pydjinni__package__swiftpackage__publish__username=bar
pydjinni__package__swiftpackage__publish__password=<password>
```
