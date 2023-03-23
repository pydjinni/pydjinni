# Development

## Local development

Install an editable version of the executable:

```shell
pip install -e .
```

When running the `pydjinni` command, it will always execute the latest code in the local repository.

## Build documentation

```shell
pip install -e .
pip install pydjinni[doc]
python -m mkdocs serve
```
