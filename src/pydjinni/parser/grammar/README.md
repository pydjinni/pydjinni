# ANTLR Usage Instructions

The Python files in this directory have been generated by ANTLR from `Idl.g4`.
Do not modify them by hand!

## Installation

ANTLR can be installed by running `pip install .[dev]`. This installs the `antlr4-tools` helper.

The `antlr4` command automatically installs the ANTLR Java binary on first execution.
If the installation fails, consult the [`antlr4-tools` documentation](https://github.com/antlr/antlr4-tools).

## Updating Lexer/Parser Sources

To regenerate the lexer and parser Python code after a change to the grammar file, 
execute `antlr4 -v <version> -Dlanguage=Python3 -visitor -no-listener Idl.g4`, where `<version>` must be set to the
installed `antlr4-python3-runtime` version.

Check the installed antlr4 python runtime by running `pip show antlr4-python3-runtime --version`.

## Auto-Update

In PyCharm Professional, the sources are automatically regenerated if the 
["File Watcher"](https://www.jetbrains.com/help/pycharm/using-file-watchers.html) plugin is available.


