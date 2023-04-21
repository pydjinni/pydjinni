# Development

## Local development

Install an editable version of the executable:

```shell
pip install -e .
```

When running the `pydjinni` command, it will always execute the latest code in the local repository.

## Execute tests

To execute the tests, first make sure that the required dependencies are installed:
```shell
pip install .[dev]
```

The tests can then be executed with `pytest`:

```shell
pytest
```

## Build documentation

```shell
pip install -e .
pip install .[doc]
python -m mkdocs serve
```
