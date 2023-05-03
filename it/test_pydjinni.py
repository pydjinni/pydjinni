import os
import subprocess
from pathlib import Path

import pytest


def pydjinni_generate(
        idl: str,
        languages: list[str],
        config: str = None,
        options: list[str] = None,
        clean: bool = None,
        cwd: Path = Path(".")):
    """
    Helper function to easily execute pydjinni generation
    Args:
        idl: The IDL file that should be processed
        languages: A list of languages that should be targeted
        config: The config file that should be used
        options: Additional options that need to be set
        clean: Whether a "clean" generation should be done. Will pass the '--clean' flag to generate.
        cwd: The working directory from which the command should be executed. Defaults to the current directory.
             Must be a Path() relative to the 'it' directory.

    """
    # Allow test execution from both root of the project and the "it" folder
    if Path(os.getcwd()).name != "it":
        cwd = Path(os.getcwd()) / "it" / cwd
    print("")
    command = ["pydjinni"]
    if config:
        command.append(f"--config {config}")
    if options:
        for option in options:
            command.append(f"--option {option}")
    command.append("generate")
    if clean:
        command.append("--clean")
    command.append(idl)
    for language in languages:
        command.append(language)
    try:
        print(f"> {' '.join(command)}")
        print(subprocess.check_output(command, cwd=cwd, stderr=subprocess.PIPE, universal_newlines=True))
    except subprocess.CalledProcessError as e:
        print(e.output)
        print(e.stderr)
        raise e


def test_pydjinni_successful_run():
    pydjinni_generate("test.djinni", ["cpp", "java"], cwd=Path("resources"))


def test_pydjinni_missing_idl():
    # GIVEN an IDL that does not exist
    idl = "unknown.djinni"
    # WHEN calling 'pydjinni generate'
    # THEN execution should fail with return code 2
    with pytest.raises(subprocess.CalledProcessError) as e:
        pydjinni_generate(idl, [], cwd=Path("resources"))
    assert e.value.returncode == 2
