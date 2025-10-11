# Build Plugin

To register a build plugin, register the `pydjinni.builder` entry-point in the plugins `pyproject.toml`:

```toml
[project.entry-points.'pydjinni.builder']
foo = 'myplugin.foo:FooTarget'
```

Pydjinni will now automatically load the plugin, once it is installed.

## Target

::: pydjinni.builder.target.BuildTarget
    options:
        summary: true
        show_source: false
        show_root_heading: false
        heading_level: 3
        show_symbol_type_toc: true
        show_signature_annotations: true
        filters:
            - "!^_"
            - "!^__"

