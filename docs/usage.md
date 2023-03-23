# Usage

PyDjinni aims to support the full development process of a cross-language
library written in C++. It does so by making a lot of opinionated presumptions along the way.

It also comes with a flexible plugin system that allows to adapt certain behaviour to the needs of your own requirements.

If the development process provided does not fit your needs nevertheless, it is still possible to
just use the `pydjinni generate` command set and ignore all the other tools in the swiss knife.

## Init

Initialize a new project setup with everything configured to work properly:

```shell
pydjinni init conan
```

Currently only the `conan` template is available.

## Generate

Generate java language bindings for android from the `foo.djinni` IDL file:

```bash
pydjinni generate foo.djinni java
```

Generate objc bindings with custom config:

```bash
pydinni generate --config=.pydjinni.yaml foo.djinni objc
```

## Build

```
pydjinni build --debug android --arch x86_64 armv8
pydjinni build ios --arch x86_64 armv8 macos --arch armv8
pydjinni build windows
```

## Package

```
pydjinni package aar
pydjinni package swiftpackage
pydjinni package nuget
pydjinni package npm
pydjinni package crate
```

## Publish

```shell
pydjinni publish aar
pydjinni publish swiftpackage
pydjinni publish nuget
pydjinni publish npm
pydjinni publish crate
```


## Config file

```yaml
djinni:
  generate:
    java:
      out: lib/djinni-generated/java
      package: pro.jothe.test
    jni:
      out: lib/djinni-generated/jni
    objc:
      out: lib/djinni-generated/objc
  build:
  	android:
  		architectures: [x86_64, armv8]
  	macos:
  		architectures: [v86_64, armv8]
  	ios:
  		architectures: [armv8]
  package:
    nuget:
      target: WindowsTarget
      target_dir: lib/platform/windows
    aar:
      target: AndroidTarget
      target_dir: lib/platform/android
    xcframework:
      target: MacosTarget
      target_dir: lib/platform/darwin/macos
      
    
```

