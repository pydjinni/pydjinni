import os
import subprocess
from pathlib import Path

import pytest


def run(test_name: str):
    """
    Executes a CMake test and fails if the return code of the CMake call is not equal to 0
    Args:
        test_name: name of the CMake test to call
    """
    # Allow test execution from within "it" folder
    working_directory = Path(__file__).parent
    print("")
    try:
        print(subprocess.check_output(["cmake", "--log-level", "DEBUG", "-P", f"{test_name}.cmake"], cwd=working_directory, stderr=subprocess.PIPE, universal_newlines=True))
    except subprocess.CalledProcessError as e:
        print(e.output)
        print(e.stderr)
        raise e


def test_generate_success():
    run("test_generate_success")


def test_generate_error():
    with pytest.raises(subprocess.CalledProcessError) as e:
        run("test_generate_error")
    assert "Error 150" in e.value.stderr


def test_changed_working_directory():
    run("test_changed_working_directory")


def test_custom_options():
    run("test_custom_options")


def test_no_config():
    with pytest.raises(subprocess.CalledProcessError) as e:
        run("test_no_config")
    assert "Error 2" in e.value.stderr


def test_just_options():
    run("test_just_options")
