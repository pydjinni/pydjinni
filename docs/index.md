---
title: PyDjinni
hide:
  - navigation
  - toc
  - footer
---
<center>

<div class="hero" markdown>

<img src="assets/logo.png" alt="logo" width="90" height="90">
<h1 class="hero-title">Integrate C++ code into<br>your Android or iOS application!</h1>
PyDjinni is a tool for generating cross-language type declarations and interface bindings.<br>
Heavily inspired by the original [Djinni by Dropbox](https://github.com/dropbox/djinni), it's designed to connect C++ with Java and Objective-C.

<br>
[&nbsp;&nbsp;:material-rocket-launch-outline: Get Started&nbsp;&nbsp;](installation.md){ .md-button .md-button--primary }&nbsp;
[:octicons-comment-discussion-16: Discuss](https://github.com/pydjinni/pydjinni/discussions){ .md-button }&nbsp;
[:simple-github: Contribute](https://github.com/pydjinni/pydjinni){ .md-button }

</div>
</center>
<br>

```{ .djinni .text .left }
# comment
person = record { # (1)!
    id: i16;
    name: str;
    age: i16;
}


database = main interface +cpp { # (2)!
    add(person: person) -> bool;
    remove(person: person) -> bool;
    get_persons() -> list<person>;
}
```

1. This defines a custom datatype that can be used to transmit complex datastructures
   from the host language to C++ und vice-versa.
2. This Interface defines a class with methods that will be implemented in C++ and can
   be called from the host language.

## Easy Interface Definition

The Djinni IDL allows to define the interface between the host language and C++ with a clean and intuitive syntax.

Datatypes are automatically converted, and interface calls are forwarded across the languages magically.

[:material-lightbulb-on-10: Learn more](idl.md){ .md-button }

<div class="clear"></div>
<br>
<br>
<br>


```{ .yaml .left }
generate:
  list_out_files: generated-files.txt
  cpp:
    out: 
      header: out/include
      source: out/src
    namespace: my::lib
  java:
    out: out/java
  jni:
    out: out/jni
```


## Flexible Configuration

The output can be configured comfortably with a YAML configuration file.

Optionally, options can also be passed to the command line interface directly, like in the original Djinni.

[:material-format-list-bulleted: Configuration Reference](config.md){ .md-button }

<div class="clear"></div>
<br>
<br>
<br>


```{ .toml .left }
[project]
name = "pydjinni-go"
description = "Plugin to add Go support"


[project.entry-points.'pydjinni.generator']
go = 'pydjinni-go.generator.go:GoTarget'
```


## Extendable

Pydjinni is modular, additional capabilities can be added through custom modules.

That way for example support for an additional host language can be added without having to maintain a fork or contributing 
to the project.

<div class="clear"></div>
<br>
<br>
<br>


```{ .python .left }
from pydjinni import API

API() \
    .configure("pyyjinni.yaml") \
    .parse("my_lib.djinni") \
    .generate("cpp") \
    .generate("java") \
    .write_out_files()
```

## Python API

The tools functionality can also be used from a Python API, in order to seamlessly embed into custom build processes.

[:material-power-plug-outline: API Documentation](api.md){ .md-button }

<div class="clear"></div>
<br>
<br>
<br>
<center>

# Roadmap

PyDjinni is written completely from scratch and still has some rough edges.<br>
Here is what is planned for the near future:


<div id="roadmap" markdown>
- [x] Publish Initial Preview
- [ ] Add C#/Windows support
- [ ] Release stable version 1.0
- [ ] Publish IDE Plugins
- [ ] Add more language bindings
</div>

<br>
<br>


[&nbsp;&nbsp;Try Now &nbsp; :material-arrow-right:&nbsp;&nbsp;](installation.md){ .md-button .md-button--primary .try-now-button }

</center>
<br>
