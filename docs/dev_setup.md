# Development Setup

## Local development

Install an editable version of the executable and all development-dependencies:

```shell
pip install -e .
pip install --group test
```

When running the `pydjinni` command, it will always execute the latest code in the local repository.

## Testing

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
pip install --group doc
python -m mkdocs serve
```

## VS Code

When developing in a virtual environment, install `antlr-tools` in the base Python environment used by Visual Studio Code to enable automatic generation of ANTLR4 files. This manual installation is not needed when developing outside a virtual environment:

```shell
pip install antlr-tools
```
