# Template Plugin

To register a template plugin that can be used to initialize a new project setup with the setup wizard, 
register the `pydjinni.builder` entry-point in the plugins `pyproject.toml`:

```toml
[project.entry-points.'pydjinni.init']
foo = 'myplugin.foo:FooTarget'
```

Where `FooTarget` is implementing the `TemplateTarget` interface.

Pydjinni will now automatically load the plugin, once it is installed.

## TemplateTarget

::: pydjinni_init.templates.target.TemplateTarget
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

