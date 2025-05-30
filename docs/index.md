---
title: PyDjinni
hide:
  - navigation
  - toc
  - footer
---

<h1 class="hero-title">PyDjinni</h1>
<h1 class="hero-subtitle">The C++ Cross-Platform Library<br>Development Toolkit.</h1>
<p class="hero-abstract" markdown>
PyDjinni is a tool for generating cross-language type declarations and interface bindings.<br>
Heavily inspired by the original [Djinni by Dropbox](https://github.com/dropbox/djinni), it's designed to connect C++ with Java, Objective-C and C#.
</p>

<div class="hero-buttons" markdown>
[&nbsp;&nbsp;:material-rocket-launch-outline: Get Started&nbsp;&nbsp;](installation.md){ .md-button .md-button--primary }
[:octicons-comment-discussion-16: Discuss](https://github.com/pydjinni/pydjinni/discussions){ .md-button }
[:simple-github: Contribute](https://github.com/pydjinni/pydjinni){ .md-button }
</div>

<br>

<div class="main-feature-panels" markdown>

<div class="feature-panel" markdown>

<h3><span class="feature-icon">💬</span>Interface Definition</h3>

The interface to C++ is defined with a custom interface definition language.

```pydjinni
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

1. This `record` defines a custom datatype that can be used to transmit data
   from the host language to C++ und vice-versa.
2. This `interface` defines a class with methods that will be implemented in C++ and can
   be called from the host language.

</div>

<div class="feature-panel" markdown>

<h3><span class="feature-icon">🎛️</span>Configuration</h3>

The output can be configured with a YAML configuration file.

```{ .yaml }
generate:
  list_processed_files: processed-files.json # (1)!
  cpp:
    out:
      header: out/include # (2)!
      source: out/src
    namespace: my::lib
  java:
    out: out/java
  jni:
    out: out/jni
```

1. A JSON report is generated that lists all input and output files.
2. The target directory for both header and source files can be specified separately

</div>

</div>

<div class="secondary-feature-panels" markdown>

<div class="feature-panel" markdown>

<h3><span class="feature-icon">🔌</span>Modular</h3>

Pydjinni is modular. Additional capabilities can be added through custom plugins.

</div>

<div class="feature-panel" markdown>

<h3><span class="feature-icon">🔧️</span>Toolchain</h3>

The tool provides additional utilities to help build, package and distribute cross-platform libraries.

</div>

<div class="feature-panel" markdown>

<h3><span class="feature-icon">🐍</span>Python API</h3>

The tool can also be used through a Python API, in order to seamlessly embed into a custom build process.

</div>

</div>

<br>
<br>

<center markdown>

# Roadmap

PyDjinni is written completely from scratch and still has some rough edges.<br>
Here is what is planned for the near future:

<div id="roadmap" markdown>
- [x] Publish initial preview
- [x] Add C#/Windows support
- [x] Add language server (LSP) support
- [x] Publish IDE plugins
- [x] Add project setup wizard
- [x] Add seamless async (coroutine) interaction
- [x] Add advanced exception translation
- [ ] Increase test coverage
- [ ] Add properties support
- [ ] Add code documentation generator
- [ ] Release stable version 1.0

</div>

<br>
<br>

[&nbsp;&nbsp;Try Now &nbsp; :material-arrow-right:&nbsp;&nbsp;](installation.md){ .md-button .md-button--primary .try-now-button }

</center>
<br>
