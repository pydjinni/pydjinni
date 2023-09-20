# Package Plugin

To register a build plugin, register the `pydjinni.packaging` entry-point in the plugins `pyproject.toml`:

```toml
[project.entry-points.'pydjinni.packaging']
foo = 'myplugin.foo:FooTarget'
```

Pydjinni will now automatically load the plugin, once it is installed.

## Target

::: pydjinni.packaging.target.PackageTarget
    options:
        show_source: false
        show_root_heading: false
        heading_level: 3

