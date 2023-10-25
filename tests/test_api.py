# Copyright 2023 jothepro
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import uuid
from pathlib import Path

import pytest
import tomli_w
import yaml

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
    list_processed_files = tmp_path / 'processed-files.yaml'
    cpp_out = tmp_path / 'out'
    api, input_file = given(
        tmp_path=tmp_path,
        config={
            'generate': {
                'list_processed_files': list_processed_files,
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
    api.parse(input_file).generate("cpp").write_processed_files()

    # THEN the expected output files should have been generated
    expected_header = cpp_out / 'foo.hpp'
    assert expected_header.exists()

    processed_files = yaml.safe_load(list_processed_files.read_text())

    # THEN 'processed-files.yaml' should contain the generated file
    assert str(expected_header) in processed_files['generated']['cpp']['header']

    # THEN 'processed-files.yaml' should contain the parsed IDL file
    assert str(input_file) in processed_files['parsed']['idl']


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


config_file_content = {
        'generate': {
            'cpp': {
                'out': 'cpp_out'
            }
        }
    }


@pytest.mark.parametrize("filename,content", [
    ("pydjinni.yaml", yaml.dump(config_file_content)),
    ("pydjinni.yml", yaml.dump(config_file_content)),
    ("pydjinni.json", json.dumps(config_file_content)),
    ("pydjinni.toml", tomli_w.dumps(config_file_content))
])
def test_API_config_file(tmp_path, filename, content):
    # GIVEN an API instance
    api = API()

    # AND GIVEN a YAML config file
    config_file = tmp_path / filename
    config_file.write_text(content)

    # WHEN configuring the API
    context = api.configure(config_file)

    # THEN the context should be configured
    assert context.config.generate.cpp.out == Path("cpp_out")


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


def test_API_invalid_config_file_extension(tmp_path: Path):
    # GIVEN an API instance
    api = API()
    file = tmp_path / "config.txt"
    file.touch()

    # WHEN configuring the API with a config file with unknown file extension
    # THEN a ConfigurationException should be raised
    with pytest.raises(ConfigurationException):
        api.configure(file)


def test_API_missing_config_file(tmp_path):
    # GIVEN an API instance
    api = API()

    # AND GIVEN a path to a file that does not exist
    nonexistent_path = tmp_path / "foo.yaml"

    # WHEN configuring the API
    # THEN a FileNotFoundException should be raised
    with pytest.raises(FileNotFoundException):
        api.configure(path=nonexistent_path)


