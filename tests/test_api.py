import uuid
from pathlib import Path

import pytest

from pydjinni import API
from pydjinni.exceptions import ConfigurationException, FileNotFoundException


def given(tmp_path: Path, config: dict, input_idl: str) -> tuple[API.ConfiguredContext, Path]:
    # GIVEN an API with a configuration
    api = API().configure(options=config)

    # AND GIVEN an input file
    input_file = tmp_path / f"{uuid.uuid4()}.djinni"
    input_file.write_text(input_idl)
    return api, input_file


def test_API_generate(tmp_path: Path):
    list_out_files = tmp_path / 'generated-files.txt'
    cpp_out = tmp_path / 'out'
    api, input_file = given(
        tmp_path=tmp_path,
        config={
            'generate': {
                'list_out_files': list_out_files,
                'cpp': {
                    'out': cpp_out,
                    'identifier': {
                        'file': 'none'
                    }
                }
            }
        },
        input_idl="""
        foo = enum {
            bar;
        }
        """
    )

    # WHEN parsing the IDL input and generating some output
    api.parse(input_file).generate("cpp").write_out_files()

    # THEN the expected output files should have been generated
    expected_header = cpp_out / 'foo.hpp'
    assert expected_header.exists()

    # THEN 'generated-files.txt' should contain the generated file
    assert str(expected_header) in list_out_files.read_text()


def test_API_no_config():
    # WHEN giving no configuration
    # THEN a ConfigurationException should be raised
    with pytest.raises(ConfigurationException):
        given(tmp_path=None, config=None, input_idl="")


def test_API_insufficient_config(tmp_path):
    # WHEN missing required configuration
    api, input_file = given(
        tmp_path=tmp_path,
        config={
            'generate': {}
        },
        input_idl="""
        foo = enum {
            bar;
        }
        """
    )

    # WHEN generating a target that has not been configured
    # THEN a ConfigurationException should be raised
    with pytest.raises(ConfigurationException):
        api.parse(input_file).generate("cpp")


def test_API_invalid_config_dict(tmp_path):
    # WHEN providing an invalid configuration
    # THEN a ConfigurationException should be raised
    with pytest.raises(ConfigurationException):
        given(
            tmp_path=tmp_path,
            config={
                'baz': {}
            },
            input_idl=""
        )


def test_API_invalid_config_file(tmp_path):
    # GIVEN an API instance
    api = API()

    # AND GIVEN a config file that cannot be parsed
    config_file = tmp_path / "pydjinni.yaml"
    config_file.write_text("***")

    # WHEN configuring the API
    # THEN a ConfigurationException should be raised
    with pytest.raises(ConfigurationException):
        api.configure(config_file)


def test_API_missing_config(tmp_path):
    # GIVEN an API instance
    api = API()

    # AND GIVEN a path to a file that does not exist
    nonexistent_path = tmp_path / "foo.yaml"

    # WHEN configuring the API
    # THEN a FileNotFoundException should be raised
    with pytest.raises(FileNotFoundException):
        api.configure(path=nonexistent_path)
