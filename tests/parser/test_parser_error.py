# Copyright 2024 jothepro
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

from pathlib import Path

from pydjinni.parser.ast import Interface, ErrorDomain
from test_parser import given, when, assert_field


def assert_error_code(error_code: ErrorDomain.ErrorCode, name: str, parameters: list[(str, str)] = None):
    assert error_code.name == name
    if parameters:
        assert len(error_code.parameters) == len(parameters)
        for index, parameter in enumerate(parameters):
            assert error_code.parameters[index].name == parameter[0]
            assert error_code.parameters[index].type_ref.name == parameter[1]
    else:
        assert len(error_code.parameters) == 0

def test_parsing_error(tmp_path: Path):
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
        foo = error {
            bar;
            baz(param: i8);
        }
        """
    )

    error_domain = when(parser, ErrorDomain, "foo")

    error_codes: list[ErrorDomain.ErrorCode] = error_domain.error_codes

    # THEN the record should have exactly 2 fields
    assert len(error_codes) == 2
    assert_error_code(error_codes[0], "bar")
    assert_error_code(error_codes[1], "baz", [("param", "i8")])

def test_parsing_error_comment(tmp_path: Path):
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
            # This is an error domain with a comment
            foo = error {
                # This is an error code
                baz;
            }
            """
    )

    # WHEN parsing the input
    error_domain = when(parser, ErrorDomain, "foo")

    # THEN the record should contain the given comment
    assert error_domain.comment == "This is an error domain with a comment"

    # THEN the field should contain the given comment
    assert error_domain.error_codes[0].comment == "This is an error code"

def test_parsing_error_no_codes(tmp_path: Path):
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
            foo = error {}
            """
    )

    error = when(parser, ErrorDomain, "foo")

    # THEN the record should have no error codes
    assert len(error.error_codes) == 0

