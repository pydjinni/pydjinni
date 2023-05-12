# Development Setup

## Local development

Install an editable version of the executable:

```shell
pip install -e .
```

When running the `pydjinni` command, it will always execute the latest code in the local repository.

## Testing

### Python Tests

To execute the tests, first make sure that the required dependencies are installed:
```shell
pip install .[dev]
```

The tests can then be executed with `pytest`:

```shell
pytest tests
```

### CMake Module Tests

```shell
pytest cmake
```

### Native Unit- and Integration-Tests

```shell
cmake -B build
cmake --build build
ctest --test-dir build
```

## Build documentation

```shell
pip install -e .
pip install .[doc]
python -m mkdocs serve
```
