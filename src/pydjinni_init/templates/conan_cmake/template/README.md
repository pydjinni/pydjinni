# {{ target }}

## Prerequisites

#> if "android" in platforms
### Android

- `ANDROID_HOME` must be set to an Android SDK installation on your device.
- `JAVA_HOME` must be set to a Java installation >= Java 17.

#### Windows

- `MinGW Makefiles` are used for the build. Install `MinGW` and make sure the `make` command (`mingw32-make`) is installed.

#> endif
## Build Instructions

- Install the Python dependencies:
  ```sh
  pip install -r requirements.txt
  ```
- Run the PyDjinni package commands to build for the different target platforms:
  ```sh
  #> if "android" in platforms:
  pydjinni package aar android
  #> endif
  #> if "darwin" in platforms:
  pydjinni package swiftpackage ios ios_simulator macos
  #> endif
  #> if "windows"in platforms:
  pydjinni package nuget windows
  #> endif
  ```
