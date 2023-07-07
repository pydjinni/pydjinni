# Generator Plugin

To register a generator plugin, register the `pydjinni.generator` entry-point in the plugins `pyproject.toml`:

```toml
[project.entry-points.'pydjinni.generator']
foo = 'myplugin.foo:FooTarget'
```

Pydjinni will now automatically load the plugin, once it is installed.

## Marshal

::: pydjinni.generator.marshal.Marshal
    options:
        show_source: false
        show_root_heading: false
        heading_level: 3
