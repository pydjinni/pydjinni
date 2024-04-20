# Project Setup

To start a new project with PyDjinni, you can either use the [PyDjinni Project Template](https://github.com/pydjinni/pydjinni-project-template)
adapt it to your needs, or you can bootstrap a new project with the `project-init` setup wizard.

## Project Template

The project template showcases how to use PyDjinni together with Conan and CMake to configure and build a cross-platform
library.

[:octicons-repo-template-16: Use the template](https://github.com/pydjinni/pydjinni-project-template){ .md-button target=_blank }

## Setup Wizard

The setup wizard can be used to bootstrap a simple project setup from scratch.
It will ask you a few questions and then create a minimal working project setup for using PyDjinni together with Conan
and CMake.

```sh
pydjinni-init conan-cmake
```

## Stay curious!

While both methods of setting up a new projects currently only support CMake with Conan, PyDjinni is designed to be
flexible and extendable.


If for some reason the given technology stack doesn't work for you, it is possible to add support for any other build 
system by developing a custom [build plugin](build_plugin.md).
