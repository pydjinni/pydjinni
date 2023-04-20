# Plugins

Pydjinni aims to provide a flexible architecture that can easily be extended with custom plugins.

Plugins are registered with setuptools [Entry Points](https://setuptools.pypa.io/en/latest/userguide/entry_point.html#entry-points-for-plugins).


## Generator Plugins

To register a generator plugin, register the `pydjinni.generator` entry-point in the plugins `pyproject.toml`:

```toml
[project.entry-points.'pydjinni.generator']
foo = 'myplugin.foo:FooTarget'
```

Pydjinni will now automatically load the plugin, once it is installed.
