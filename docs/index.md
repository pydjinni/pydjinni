---
title: PyDjinni
hide:
  - navigation
  - toc
  - footer
---
<center>

<img src="assets/logo.png" alt="logo" width="90" height="90">
<h1 class="hero-title">Integrate C++ code into<br>your Java, Objective-C or C# application!</h1>
PyDjinni is a tool for generating cross-language type declarations and interface bindings.<br>
Heavily inspired by the original [Djinni by Dropbox](https://github.com/dropbox/djinni), it's designed to connect C++ with either Java, Objective-C, Rust or C#.

[:material-rocket-launch-outline: Get Started](installation.md){ .md-button .md-button--primary }
[:octicons-comment-discussion-16: Discuss](https://github.com/pydjinni/pydjinni/discussions){ .md-button }
[:simple-github: Contribute](https://github.com/pydjinni/pydjinni){ .md-button }


<br>
<br>
<br>

:octicons-chevron-down-12:

<br>
<br>
</center>
<hr>
<br>

<div class="left">

```
person = record {
    id: i16;
    name: str;
    age: i16;
}


database = interface +c {
    add(person: person): bool;
    remove(person: person): bool;
    get_persons(): list<person>;
}
```

</div>

## Easy Interface Definition

The Djinni IDL allows to define the interface between the host language and C++ with a clean and intuitive syntax.

Datatypes are automatically converted, and interface calls are forwarded across the languages magically.

[:material-lightbulb-on-10: Learn more](idl.md){ .md-button }

<div class="clear"></div>
<br>
<br>

<div class="left">

```yaml
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

</div>

## Flexible Configuration

The output can be configured comfortably with a YAML configuration file.

Optionally, options can also be passed to the command line interface directly, like in the original Djinni.

[:material-format-list-bulleted: Configuration Reference](config.md){ .md-button }

<div class="clear"></div>
<br>
<br>

<div class="left">

```toml
[project]
name = "pydjinni-go"
description = "Plugin to add Go support"


[project.entry-points.'pydjinni.generator']
go = 'pydjinni-go.generator.go:GoTarget'
```

</div>

## Extendable

Pydjinni is modular, additonal capabilities can be added through custom modules.

That way for example support for an additional host language can be added without having to maintain a fork or contributing 
to the project.

<div class="clear"></div>
<br>
<br>

<div class="left">

```python
from pydjinni import API

API() \
    .configure("pyyjinni.yaml") \
    .parse("my_lib.djinni") \
    .generate("cpp") \
    .generate("java") \
    .write_out_files()
```

</div>

## Python API

The tools functionality can also be used from a Python API, in order to seamlessly embed into custom build processes.

[:material-power-plug-outline: API Documentation](api.md){ .md-button }

<div class="clear"></div>
<br>
<br>
<br>
<center>

[&nbsp;&nbsp;Try Now &nbsp; :material-arrow-right:&nbsp;&nbsp;](installation.md){ .md-button .md-button--primary }

</center>
<br>
